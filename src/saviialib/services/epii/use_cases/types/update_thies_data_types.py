from dataclasses import dataclass, field
from typing import Dict
from saviialib.general_types.api.epii_api_types import FtpClientConfig, SharepointConfig


@dataclass
class UpdateThiesDataUseCaseInput:
    ftp_config: FtpClientConfig
    sharepoint_config: SharepointConfig


@dataclass
class UpdateThiesDataUseCaseOutput:
    message: str
    status: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)
