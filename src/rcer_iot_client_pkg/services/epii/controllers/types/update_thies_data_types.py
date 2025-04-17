from dataclasses import dataclass, field
from typing import Dict


@dataclass
class UpdateThiesDataControllerInput:
    ftp_host: str
    ftp_port: str
    ftp_user: str
    ftp_password: str


@dataclass
class UpdateThiesDataControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
