from aioftp import Client

from rcer_iot_client_pkg.libs.ftp_client.ftp_client_contract import (
    FTPClientContract,
)
from rcer_iot_client_pkg.libs.ftp_client.types.ftp_client_types import (
    FtpClientInitArgs,
    ListFilesArgs,
    ReadFileArgs,
)


class AioFTPClient(FTPClientContract):
    def __init__(self, args: FtpClientInitArgs) -> None:
        self.host = args.host
        self.port = args.port
        self.password = args.password
        self.user = args.user
        self.client = Client()

    async def _async_start(self) -> None:
        try: 
            await self.client.connect(host=self.host, port=self.port)
            await self.client.login(user=self.user, password=self.password)
        except Exception:
            raise RuntimeError("Unexpected error occurred while trying to connect to the FTP server")

    async def list_files(self, args: ListFilesArgs) -> list[str]:
        await self._async_start()
        return [
            path.name async for path, _ in self.client.list(args.path, recursive=False)
        ]

    async def read_file(self, args: ReadFileArgs) -> bytes:
        await self._async_start()
        async with self.client.download_stream(args.file_path) as stream:
            return await stream.read()
