from dataclasses import dataclass, field
from typing import Dict
from logging import Logger
from saviialib.general_types.api.saviia_thies_api_types import SaviiaThiesConfig


@dataclass
class GetThiesDataControllerInput:
    config: SaviiaThiesConfig
    ftp_host: str
    ftp_port: int
    ftp_user: str
    ftp_password: str
    sharepoint_destination_path: str = ""
    logger: Logger | None = None


@dataclass
class GetThiesDataControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
