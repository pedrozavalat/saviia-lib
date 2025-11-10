from dataclasses import dataclass, field
from typing import Dict
from saviialib.general_types.api.saviia_thies_api_types import SaviiaThiesConfig


@dataclass
class UpdateThiesDataControllerInput:
    config: SaviiaThiesConfig
    sharepoint_folders_path: list
    ftp_server_folders_path: list
    local_backup_source_path: str


@dataclass
class UpdateThiesDataControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
