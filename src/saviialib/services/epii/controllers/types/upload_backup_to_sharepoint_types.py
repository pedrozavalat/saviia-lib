from dataclasses import dataclass, field
from typing import Dict

from saviialib.general_types.api.epii_api_types import EpiiSharepointBackupConfig


@dataclass
class UploadBackupToSharepointControllerInput:
    config: EpiiSharepointBackupConfig


@dataclass
class UploadBackupToSharepointControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
