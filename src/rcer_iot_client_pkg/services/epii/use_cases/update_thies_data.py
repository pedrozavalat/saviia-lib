from dotenv import load_dotenv

import rcer_iot_client_pkg.services.epii.use_cases.constants as c
from rcer_iot_client_pkg.general_types.error_types.api.update_thies_data_error_types import (
    FetchCloudFileNamesError,
    FetchThiesFileContentError,
    ThiesUploadEmptyError,
)
from rcer_iot_client_pkg.general_types.error_types.common import (
    EmptyDataError,
    FtpClientError,
    HttpClientError,
)
from rcer_iot_client_pkg.libs.async_http_client import (
    AsyncHTTPClient,
    AsyncHttpClientInitArgs,
    GetArgs,
)
from rcer_iot_client_pkg.libs.ftp_client import (
    FTPClient,
    FtpClientInitArgs,
    ListFilesArgs,
    ReadFileArgs,
)
from rcer_iot_client_pkg.services.epii.use_cases.types import (
    UpdateThiesDataUseCaseInput,
)
from rcer_iot_client_pkg.services.epii.utils import (
    generate_file_content,
)

load_dotenv()


class UpdateThiesDataUseCase:
    def __init__(self, input: UpdateThiesDataUseCaseInput):
        self.ftp_port = input.ftp_port
        self.ftp_host = input.ftp_host
        self.ftp_password = input.ftp_password
        self.ftp_user = input.ftp_user
        self.sharepoint_client = self._initialize_sharepoint_client()
        self.thies_ftp_client = self._initialize_thies_ftp_client()
        self.uploading = set()

    def _initialize_sharepoint_client(self) -> AsyncHTTPClient:
        """Initialize the HTTP client."""
        try:
            return AsyncHTTPClient(
                AsyncHttpClientInitArgs(
                    client_name="aiohttp_client",
                    access_token="temporal-token",
                    base_url="https://graph.microsoft.com/v1.0/",
                )
            )
        except ConnectionError as error:
            raise HttpClientError(error)

    def _initialize_thies_ftp_client(self) -> FTPClient:
        """Initialize the FTP client."""
        try:
            return FTPClient(
                FtpClientInitArgs(
                    client_name="aioftp_client",
                    host=self.ftp_host,
                    user=self.ftp_user,
                    password=self.ftp_password,
                    port=self.ftp_port,
                )
            )
        except RuntimeError as error:
            raise FtpClientError(error)

    async def fetch_cloud_file_names(self, folder_name: str) -> set[str]:
        """Fetch file names from the RCER cloud."""
        try:
            cloud_files = set()
            async with self.sharepoint_client:
                for file_type in c.FILE_TYPES:
                    destination_path = f"Onedrive_UC/noveno-semestre/IPRE-RCER/{folder_name}/{file_type}"
                    endpoint = f"drives/{c.DRIVE_ID}/root:/{destination_path}:/children"
                    response = await self.sharepoint_client.get(
                        GetArgs(endpoint=endpoint)
                    )
                    cloud_files.update(
                        {f"{file_type}_{item['name']}" for item in response["value"]}
                    )
            return cloud_files
        except ConnectionError as error:
            raise FetchCloudFileNamesError(error)

    async def fetch_thies_file_names(self) -> set[str]:
        """Fetch file names from the THIES FTP server."""
        try:
            avg_files = await self.thies_ftp_client.list_files(
                ListFilesArgs(path=c.PATH_AVG_FILES)
            )
            ext_files = await self.thies_ftp_client.list_files(
                ListFilesArgs(path=c.PATH_EXT_FILES)
            )
            return {f"AVG_{name}" for name in avg_files} | {
                f"EXT_{name}" for name in ext_files
            }
        except ConnectionError:
            raise ThiesUploadEmptyError

    async def fetch_thies_file_content(self) -> dict[str, bytes]:
        """Fetch the content of files from the THIES FTP server."""
        content_files = {}
        for file in self.uploading:
            try:
                origin, filename = file.split("_", 1)
                file_path = (
                    f"{c.PATH_AVG_FILES}/{filename}"
                    if origin == "AVG"
                    else f"{c.PATH_EXT_FILES}/{filename}"
                )
                content = await self.thies_ftp_client.read_file(ReadFileArgs(file_path))
                content_files[filename] = content
            except ConnectionError as error:
                raise FetchThiesFileContentError(error)
        return content_files

    async def execute(self) -> dict:
        """Synchronize data from the THIES Center to the cloud."""
        try:
            thies_files = await self.fetch_thies_file_names()
        except RuntimeError as error:
            raise FtpClientError(error)

        cloud_files = await self.fetch_cloud_file_names(folder_name="thies")
        self.uploading = thies_files - cloud_files
        if not self.uploading:
            raise EmptyDataError

        thies_file_contents = await self.fetch_thies_file_content()
        data = generate_file_content(thies_file_contents)
        return data
