import ftplib
import asyncio
from io import BytesIO
from saviialib.libs.ftp_client.ftp_client_contract import (
    FTPClientContract,
)
from saviialib.libs.ftp_client.types.ftp_client_types import (
    FtpClientInitArgs,
    FtpListFilesArgs,
    FtpReadFileArgs,
)


class FtplibClient(FTPClientContract):
    def __init__(self, args: FtpClientInitArgs) -> None:
        self.host = args.config.ftp_host
        self.port = args.config.ftp_port
        self.password = args.config.ftp_password
        self.user = args.config.ftp_user
        self.client = ftplib.FTP(host=self.host, user=self.user, passwd=self.password)

    async def _async_start(self) -> None:
        try:
            await asyncio.to_thread(self.client.login, self.user, self.password)
        except OSError:
            raise ConnectionRefusedError(
                f"{self.host}:{self.port} isn't active. "
                "Please ensure the server is running and accessible."
            )
        except Exception as error:
            raise ConnectionError(
                f"General connection for {self.host}:{self.port}.", error.__str__()
            )

    async def list_files(self, args: FtpListFilesArgs) -> list[str]:
        try:
            EXCLUDED_NAMES = [".", ".."]
            await self._async_start()
            await asyncio.to_thread(self.client.cwd, args.path)
            filenames = await asyncio.to_thread(self.client.nlst, args.path)
            return [
                filename for filename in filenames if filename not in EXCLUDED_NAMES
            ]
        except Exception as error:
            raise ConnectionAbortedError(error)

    async def read_file(self, args: FtpReadFileArgs) -> bytes:
        await self._async_start()
        try:
            file_content = BytesIO()
            await asyncio.to_thread(
                self.client.retrbinary, "RETR " + args.file_path, file_content.write
            )
            await asyncio.to_thread(file_content.seek, 0)
            file_bytes = await asyncio.to_thread(file_content.read)
            return file_bytes
        except Exception as error:
            raise FileNotFoundError(f"File not found: {args.file_path}") from error
