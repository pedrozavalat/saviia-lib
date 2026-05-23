from dataclasses import dataclass, field
from typing import Dict
from saviialib.general_types.api.saviia_thies_api_types import SaviiaThiesConfig


@dataclass
class GetThiesDataControllerInput:
    config: SaviiaThiesConfig
    ftp_host: str
    ftp_port: int
    ftp_user: str
    ftp_password: str
    sharepoint_destination_path: str = ""


@dataclass
class GetThiesDataControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
