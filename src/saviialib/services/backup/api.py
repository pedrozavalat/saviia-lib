from typing import Any, Dict

from .controllers.upload_backup_to_sharepoint import (
    UploadBackupToSharepointControllerInput,
)
from .controllers.upload_backup_to_sharepoint import UploadBackupToSharepointController
from .controllers.export_files import ExportFilesController, ExportFilesControllerInput
from saviialib.general_types.api.saviia_backup_api_types import SaviiaBackupConfig


class SaviiaBackupAPI:
    """
    EpiiAPI is a service class that provides methods to interact with Patagonia Center system.
    """

    def __init__(self, config: SaviiaBackupConfig):
        self.config = config

    async def upload_backup_to_sharepoint(
        self, local_backup_source_path: str, sharepoint_destination_path: str
    ) -> Dict[str, Any]:
        """Migrate a backup folder from Home assistant to Sharepoint directory.
        Args:
            local_backup_source_path (str): Local path to backup.
        Returns:
            response (dict): A dictionary containing the response from the upload operation.
                This dictionary will typically include information about the success or
                failure of the upload, as well as any relevant metadata.
        """

        controller = UploadBackupToSharepointController(
            UploadBackupToSharepointControllerInput(
                self.config, local_backup_source_path, sharepoint_destination_path
            )
        )
        response = await controller.execute()
        return response.__dict__

    async def export_files(
        self, local_folder_path: str, sharepoint_destination_path: str
    ) -> Dict[str, Any]:
        """Synchronize only outdated/missing files from a local backup folder to SharePoint.

        The local folder is resolved relative to `self.config.local_backup_path`.
        The SharePoint destination path is the exact target folder.
        """
        controller = ExportFilesController(
            ExportFilesControllerInput(
                config=self.config,
                local_folder_path=local_folder_path,
                sharepoint_destination_path=sharepoint_destination_path,
            )
        )
        response = await controller.execute()
        return response.__dict__
