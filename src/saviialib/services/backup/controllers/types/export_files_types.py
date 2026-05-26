from dataclasses import dataclass, field
from typing import Dict

from saviialib.general_types.api.saviia_backup_api_types import SaviiaBackupConfig


@dataclass
class ExportFilesControllerInput:
    config: SaviiaBackupConfig
    local_folder_path: str
    sharepoint_destination_path: str


@dataclass
class ExportFilesControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str | dict] = field(default_factory=dict)
