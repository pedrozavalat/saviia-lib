from dataclasses import dataclass, field
from typing import Dict

from saviialib.general_types.api.saviia_thies_api_types import SaviiaThiesConfig


@dataclass
class PostThiesDataControllerInput:
    config: SaviiaThiesConfig
    ftp_host: str
    ftp_port: int
    ftp_user: str
    ftp_password: str
    need_to_sync: bool
    need_to_backup: bool
    sharepoint_destination_path: str
    ftp_server_folders_path: list
    local_backup_source_path: str


@dataclass
class PostThiesDataControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
