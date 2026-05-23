from dataclasses import dataclass
from logging import Logger
from saviialib.libs.directory_client import DirectoryClient
from saviialib.libs.ftp_client import FTPClient
from saviialib.libs.sharepoint_client import SharepointClient
from saviialib.libs.files_client import FilesClient


@dataclass
class GetThiesDataUseCaseInput:
    ftp_client: FTPClient
    sharepoint_client: SharepointClient
    files_client: FilesClient
    directory_client: DirectoryClient
    local_backup_path: str
    logger: Logger | None = None

    sharepoint_destination_path: str = ""


@dataclass
class GetThiesDataUseCaseOutput:
    need_to_sync: bool
    need_to_backup: bool
    total_to_backup: int
    total_to_sync: int
