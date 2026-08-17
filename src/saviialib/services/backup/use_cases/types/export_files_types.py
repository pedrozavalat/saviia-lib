from dataclasses import dataclass, field
from logging import Logger

from saviialib.libs.directory_client import DirectoryClient
from saviialib.libs.cloud_client import CloudClient
from saviialib.libs.files_client import FilesClient


@dataclass
class ExportFilesUseCaseInput:
    cloud_client: CloudClient
    files_client: FilesClient
    directory_client: DirectoryClient
    local_backup_path: str
    local_folder_path: str
    cloud_provider_destination_path: str
    logger: Logger


@dataclass
class ExportFilesUseCaseOutput:
    synced_files: list[str] = field(default_factory=list)
    total_local_files: int = 0
    total_cloud_files: int = 0
    total_pending_files: int = 0
    total_synced_files: int = 0
