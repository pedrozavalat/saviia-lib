from dataclasses import dataclass, field

from saviialib.general_types.api.saviia_backup_api_types import SaviiaBackupConfig


@dataclass
class UploadBackupToSharepointControllerInput:
    config: SaviiaBackupConfig
    local_backup_source_path: str
    cloud_provider_destination_path: str


@dataclass
class UploadBackupToSharepointControllerOutput:
    message: str
    status: int
    metadata: dict[str, str] = field(default_factory=dict)
