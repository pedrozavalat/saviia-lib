import asyncio
from .types.get_miniseed_files_types import (
    GetMiniseedFilesUseCaseInput,
    GetMiniseedFilesUseCaseOutput,
)
from typing import Dict, Any
from saviialib.libs.sftp_client import (
    SFTPClient,
    SFTPClientInitArgs,
    ListfilesArgs,
    DownloadfilesArgs,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ShakesNoContentError,
)
from saviialib.general_types.error_types.common.common_types import SftpClientError
from .utils.get_miniseed_files_utils import parse_downloaded_metadata


class GetMiniseedFilesUseCase:
    def __init__(self, input: GetMiniseedFilesUseCaseInput) -> None:
        self.password = input.password
        self.username = input.username
        self.ssh_key_path = input.ssh_key_path
        self.port = input.port
        self.raspberry_shakes: Dict[str, str] = input.raspberry_shakes
        self.dir_client = DirectoryClient(DirectoryClientArgs("os_client"))

    def _initialize_sftp_client(self, ip_address: str):
        return SFTPClient(
            SFTPClientInitArgs(
                "asyncssh_sftp",
                password=self.password,
                username=self.username,
                ssh_key_path=self.ssh_key_path,
                host=ip_address,
                port=self.port,
            )
        )

    async def _download_mseed_file(self, rs_name: str, rs_ip: str) -> Dict[str, Any]:
        DEST_BASE_DIR = "./rshakes-mseed-files"
        SOURCE_PATH = self.dir_client.join_paths("opt", "data", "archive")
        local_path = self.dir_client.join_paths(DEST_BASE_DIR, rs_name)
        if not await self.dir_client.isdir(local_path):
            await self.dir_client.makedirs(local_path)
        sftp_client = self._initialize_sftp_client(rs_ip)

        local_files = await self.dir_client.listdir(local_path)
        try:
            sftp_files = await sftp_client.list_files(ListfilesArgs(path=SOURCE_PATH))
            pending_files = set(sftp_files) - set(local_files)
            if not pending_files:
                raise ShakesNoContentError

            await sftp_client.download_files(
                DownloadfilesArgs(
                    source_path=SOURCE_PATH,
                    destination_path=local_path,
                    files_to_download=list(pending_files),
                )
            )
        except ConnectionError as error:
            raise SftpClientError(reason=error)
        return {
            "rs_name": rs_name,
            "destination_path": local_path,
            "total_files": len(pending_files),
        }

    async def execute(self):
        requests = []
        for rs_name, rs_ip in self.raspberry_shakes:
            requests.append(self._download_mseed_file(rs_name, rs_ip))
        responses = await asyncio.gather(*requests, return_exceptions=True)
        return GetMiniseedFilesUseCaseOutput(
            download_status=parse_downloaded_metadata(responses),
        )
