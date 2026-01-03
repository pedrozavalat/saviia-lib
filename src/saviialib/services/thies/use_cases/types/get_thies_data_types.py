from dataclasses import dataclass, field
from typing import Dict, List, Set
from saviialib.general_types.api.saviia_api_types import (
    FtpClientConfig,
    SharepointConfig,
)


@dataclass
class GetThiesDataUseCaseInput:
    ftp_config: FtpClientConfig
    sharepoint_config: SharepointConfig
    local_backup_path: str


@dataclass
class GetThiesDataUseCaseOutput:
    need_to_sync: bool
    need_to_backup: bool
    unbacked_files: Set[str]
    unsynchronised_files: Set[str]
