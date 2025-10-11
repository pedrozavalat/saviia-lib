from dataclasses import dataclass
from saviialib.general_types.api.saviia_api_types import SharepointConfig
from logging import Logger


@dataclass
class UploadBackupToSharepointUseCaseInput:
    sharepoint_config: SharepointConfig
    local_backup_source_path: str
    sharepoint_destination_path: str
    logger: Logger
