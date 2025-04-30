from dataclasses import dataclass, field
from typing import Dict


@dataclass
class FtpClientConfig:
    ftp_host: str
    ftp_port: int
    ftp_user: str
    ftp_password: str


@dataclass
class SharepointConfig:
    sharepoint_client_id: str
    sharepoint_client_secret: str
    sharepoint_tenant_id: str
    sharepoint_tenant_name: str
    sharepoint_site_name: str


@dataclass
class UpdateThiesDataUseCaseInput:
    ftp_config: FtpClientConfig
    sharepoint_config: SharepointConfig


@dataclass
class UpdateThiesDataUseCaseOutput:
    message: str
    status: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)
