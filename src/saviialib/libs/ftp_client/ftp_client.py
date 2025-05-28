from .clients.aioftp_client import AioFTPClient
from .clients.ftplib_client import FtplibClient
from .ftp_client_contract import FTPClientContract
from .types.ftp_client_types import FtpClientInitArgs, FtpListFilesArgs, FtpReadFileArgs


class FTPClient(FTPClientContract):
    CLIENTS = {"aioftp_client", "ftplib_client"}

    def __init__(self, args: FtpClientInitArgs) -> None:
        if args.client_name not in FTPClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)

        if args.client_name == "aioftp_client":
            self.client_obj = AioFTPClient(args)
        elif args.client_name == "ftplib_client":
            self.client_obj = FtplibClient(args)
        self.client_name = args.client_name

    async def list_files(self, args: FtpListFilesArgs) -> list[str]:
        return await self.client_obj.list_files(args)

    async def read_file(self, args: FtpReadFileArgs) -> bytes:
        return await self.client_obj.read_file(args)
