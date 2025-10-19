from .sftp_client_contract import SFTPClientContract
from .types.sftp_client_types import (
    SFTPClientInitArgs,
    ListfilesArgs,
    DownloadfilesArgs,
)
from .clients.asyncssh_sftp_client import AsyncsshSFTPClient
from typing import List


class SFTPClient(SFTPClientContract):
    CLIENTS = {"asyncssh_sftp"}

    def __init__(self, args: SFTPClientInitArgs) -> None:
        if args.client_name not in SFTPClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)
        if args.client_name == "asyncssh_sftp":
            self.client_obj = AsyncsshSFTPClient(args)
        self.client_name = args.client_name

    async def list_files(self, args: ListfilesArgs) -> List[str]:
        return await self.client_obj.list_files(args)

    async def download_files(self, args: DownloadfilesArgs) -> None:
        return await self.client_obj.download_files(args)
