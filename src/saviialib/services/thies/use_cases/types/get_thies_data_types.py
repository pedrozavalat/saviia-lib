from dataclasses import dataclass
from typing import Set

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


@dataclass
class GetThiesDataUseCaseOutput:
    need_to_sync: bool
    need_to_backup: bool
    unbacked_files: Set[str]
    unsynchronised_files: Set[str]
