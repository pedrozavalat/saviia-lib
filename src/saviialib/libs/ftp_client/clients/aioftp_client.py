from aioftp import Client
from aioftp.errors import StatusCodeError
from saviialib.libs.ftp_client.ftp_client_contract import (
    FTPClientContract,
)
from saviialib.libs.ftp_client.types.ftp_client_types import (
    FtpClientInitArgs,
    FtpListFilesArgs,
    FtpReadFileArgs,
)


class AioFTPClient(FTPClientContract):
    def __init__(self, args: FtpClientInitArgs) -> None:
        self.host = args.config.ftp_host
        self.port = args.config.ftp_port
        self.password = args.config.ftp_password
        self.user = args.config.ftp_user
        self.client = Client()

    async def _async_start(self) -> None:
        try:
            await self.client.connect(host=self.host, port=self.port)
        except OSError:
            raise ConnectionRefusedError(
                f"{self.host}:{self.port} isn't active. "
                "Please ensure the server is running and accessible."
            )
        try:
            await self.client.login(user=self.user, password=self.password)
        except StatusCodeError:
            raise ConnectionAbortedError(
                "Authentication failed. Please verify your credentials and try again."
            )

    async def list_files(self, args: FtpListFilesArgs) -> list[str]:
        try:
            await self._async_start()
            files = []
            async for path, info in self.client.list(args.path, recursive=False):
                files.append((path.name, int((info.get("size", 0)))))
            return files
        except StatusCodeError as error:
            raise ConnectionAbortedError(error)

    async def read_file(self, args: FtpReadFileArgs) -> bytes:
        await self._async_start()
        try:
            async with self.client.download_stream(args.file_path) as stream:  # type: ignore
                return await stream.read()
        except StatusCodeError as error:
            raise FileNotFoundError(f"File not found: {args.file_path}") from error
