from dataclasses import dataclass
from logging import Logger
from typing import List

from saviialib.libs.directory_client import DirectoryClient
from saviialib.libs.files_client import FilesClient
from saviialib.libs.ftp_client import FTPClient
from saviialib.libs.sharepoint_client import SharepointClient


@dataclass
class PostThiesDataUseCaseInput:
    ftp_client: FTPClient
    sharepoint_client: SharepointClient
    files_client: FilesClient
    directory_client: DirectoryClient
    sharepoint_destination_path: str
    ftp_server_folders_path: List[str]
    local_backup_source_path: str
    need_to_sync: bool
    need_to_backup: bool
    logger: Logger
