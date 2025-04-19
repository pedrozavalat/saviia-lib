from dataclasses import dataclass, field
from typing import Dict


@dataclass
class UpdateThiesDataUseCaseInput:
    ftp_host: str
    ftp_port: int
    ftp_user: str
    ftp_password: str


@dataclass
class UpdateThiesDataUseCaseOutput:
    message: str
    status: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)
