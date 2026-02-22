from dataclasses import dataclass, field
from typing import Dict
from saviialib.general_types.api.saviia_thies_api_types import SaviiaThiesConfig


@dataclass
class DetectFailuresControllerInput:
    config: SaviiaThiesConfig
    local_backup_source_path: str
    db_driver: str = ""
    db_host: str = ""
    db_name: str = ""
    user: str = ""
    pwd: str = ""


@dataclass
class DetectFailuresControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
