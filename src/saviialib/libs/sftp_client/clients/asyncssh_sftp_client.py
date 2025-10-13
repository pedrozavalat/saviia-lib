from saviialib.libs.sftp_client.sftp_client_contract import SFTPClientContract
from saviialib.libs.sftp_client.types.sftp_client_types import (
    SFTPClientInitArgs,
    ListfilesArgs,
    DownloadfilesArgs,
)
from typing import Optional, List, Tuple
from saviialib.general_types.error_types.common.common_types import EmptyDataError
import asyncssh  # type: ignore
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs


class AsyncsshSFTPClient(SFTPClientContract):
    def __init__(self, args: SFTPClientInitArgs) -> None:
        self.host: str = args.host
        self.port: int = args.port
        self.username: str = args.username
        self.password: Optional[str] = args.password
        self.ssh_key_path: Optional[str] = args.ssh_key_path
        self.dir_client = DirectoryClient(DirectoryClientArgs("os_client"))
        self._validate_credentials()

    def _validate_credentials(self):
        if not self.password and not self.ssh_key_path:
            raise EmptyDataError(
                reason="At least one attribute (ssh key or password) must be provided"
            )

    async def _start_connection(
        self,
    ) -> Tuple[asyncssh.SSHClientConnection, asyncssh.SFTPClient]:
        try:
            ssh_connection = await asyncssh.connect(
                self.host,
                username=self.username,
                port=self.port,
                client_keys=[self.ssh_key_path],
                password=self.password,
            )
            sftp_client = await ssh_connection.start_sftp_client()
            return ssh_connection, sftp_client
        except (OSError, asyncssh.Error) as exc:
            raise ConnectionError("SFTP Operation failed: " + str(exc))

    async def list_files(self, args: ListfilesArgs) -> List[str]:
        ssh_conn, sftp_client = await self._start_connection()
        async with ssh_conn:
            async with sftp_client:
                files = await sftp_client.listdir(args.path)
                files = [f for f in files if f not in (".", "..")]
                return files
        await self._end_connection(ssh_conn)

    async def download_files(self, args: DownloadfilesArgs) -> None:
        ssh_conn, sftp_client = await self._start_connection()
        if not args.destination_path or not args.source_path:
            conflict_path = (
                "destination path" if not args.destination_path else "source path"
            )
            raise ConnectionError(f"The {conflict_path} must be provided.")

        download_all = len(args.files_to_download) == 0
        async with ssh_conn:
            async with sftp_client:
                if download_all:
                    await sftp_client.get(
                        args.source_path,
                        args.destination_path,
                        recurse=True,
                        preserve=True,
                    )
                else:
                    for filename in args.files_to_download:
                        source_path = self.dir_client.join_paths(
                            args.source_path, filename
                        )
                        dest_path = self.dir_client.join_paths(
                            args.destination_path, filename
                        )
                        await sftp_client.get(source_path, dest_path)

    async def _end_connection(self, connection) -> None:
        await connection.wait_closed()
