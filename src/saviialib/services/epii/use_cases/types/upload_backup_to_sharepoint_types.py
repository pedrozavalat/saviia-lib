from dataclasses import dataclass
from saviialib.general_types.api.epii_api_types import SharepointConfig
from logging import Logger


@dataclass
class UploadBackupToSharepointUseCaseInput:
    sharepoint_config: SharepointConfig
    local_backup_source_path: str
    destination_folders: dict
    logger: Logger
