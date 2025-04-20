from dotenv import load_dotenv

import rcer_iot_client_pkg.services.epii.constants.update_thies_data_constants as c
from rcer_iot_client_pkg.general_types.error_types.api.update_thies_data_error_types import (
    SharePointFetchingError,
    ThiesConnectionError,
    ThiesFetchingError,
)
from rcer_iot_client_pkg.general_types.error_types.common import (
    EmptyDataError,
    FtpClientError,
    SharepointClientError,
)
from rcer_iot_client_pkg.libs.ftp_client import (
    FTPClient,
    FtpClientInitArgs,
    FtpListFilesArgs,
    FtpReadFileArgs,
)
from rcer_iot_client_pkg.libs.sharepoint_client import (
    SharepointClient,
    SharepointClientInitArgs,
    SpListFilesArgs,
)
from rcer_iot_client_pkg.services.epii.use_cases.types import (
    UpdateThiesDataUseCaseInput,
    FtpClientConfig,
    SharepointConfig,
)
from rcer_iot_client_pkg.services.epii.utils import (
    parse_execute_response,
)

load_dotenv()


class UpdateThiesDataUseCase:
    def __init__(self, input: UpdateThiesDataUseCaseInput):
        self.sharepoint_client = self._initialize_sharepoint_client(
            input.sharepoint_config
        )
        self.thies_ftp_client = self._initialize_thies_ftp_client(input.ftp_config)
        self.uploading = set()

    def _initialize_sharepoint_client(
        self, config: SharepointConfig
    ) -> SharepointClient:
        """Initialize the HTTP client."""
        try:
            return SharepointClient(
                SharepointClientInitArgs(config, client_name="sharepoint_rest_api")
            )
        except ConnectionError as error:
            raise SharepointClientError(error)

    def _initialize_thies_ftp_client(self, config: FtpClientConfig) -> FTPClient:
        """Initialize the FTP client."""
        try:
            return FTPClient(FtpClientInitArgs(config, client_name="aioftp_client"))
        except RuntimeError as error:
            raise FtpClientError(error)

    async def fetch_cloud_file_names(self) -> set[str]:
        """Fetch file names from the RCER cloud."""

        try:
            cloud_files = set()
            async with self.sharepoint_client:
                for folder in c.SHAREPOINT_THIES_FOLDERS:
                    args = SpListFilesArgs(
                        folder_relative_url=f"{c.SHAREPOINT_BASE_URL}/{folder}"
                    )
                    response = await self.sharepoint_client.list_files(args)
                    cloud_files.update(
                        {f"{folder}_{item['Name']}" for item in response["value"]}
                    )
            return cloud_files
        except ConnectionError as error:
            raise SharePointFetchingError(reason=error)

    async def fetch_thies_file_names(self) -> set[str]:
        """Fetch file names from the THIES FTP server."""
        try:
            avg_files = await self.thies_ftp_client.list_files(
                FtpListFilesArgs(path=c.FTP_SERVER_PATH_AVG_FILES)
            )
            ext_files = await self.thies_ftp_client.list_files(
                FtpListFilesArgs(path=c.FTP_SERVER_PATH_EXT_FILES)
            )
            return {f"AVG_{name}" for name in avg_files} | {
                f"EXT_{name}" for name in ext_files
            }
        except ConnectionRefusedError as error:
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            raise ThiesFetchingError(reason=error)

    async def fetch_thies_file_content(self) -> dict[str, bytes]:
        """Fetch the content of files from the THIES FTP server."""
        try:
            content_files = {}
            for file in self.uploading:
                origin, filename = file.split("_", 1)
                file_path = (
                    f"{c.FTP_SERVER_PATH_AVG_FILES}/{filename}"
                    if origin == "AVG"
                    else f"{c.FTP_SERVER_PATH_EXT_FILES}/{filename}"
                )
                content = await self.thies_ftp_client.read_file(
                    FtpReadFileArgs(file_path)
                )
                content_files[filename] = content
            return content_files
        except ConnectionRefusedError as error:
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            raise ThiesFetchingError(reason=error)

    async def execute(self) -> dict:
        """Synchronize data from the THIES Center to the cloud."""
        try:
            thies_files = await self.fetch_thies_file_names()
        except RuntimeError as error:
            raise FtpClientError(error)
        try:
            cloud_files = await self.fetch_cloud_file_names()
        except RuntimeError as error:
            raise SharepointClient(error)
        self.uploading = thies_files - cloud_files
        if not self.uploading:
            raise EmptyDataError(reason="No files to upload.")

        thies_file_contents = await self.fetch_thies_file_content()
        data = parse_execute_response(thies_file_contents)
        return data
