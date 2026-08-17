from typing import Any, Dict


from .controllers.export_files import ExportFilesController, ExportFilesControllerInput
from saviialib.general_types.api.saviia_backup_api_types import SaviiaBackupConfig


class SaviiaBackupAPI:
    """
    EpiiAPI is a service class that provides methods to interact with Patagonia Center system.
    """

    def __init__(self, config: SaviiaBackupConfig):
        self.config = config

    async def export_files(
        self, local_folder_path: str, cloud_provider_destination_path: str
    ) -> Dict[str, Any]:
        """Synchronize only outdated/missing files from a local backup folder to cloud storage.

        The local folder is resolved relative to `self.config.local_backup_path`.
        The cloud provider destination path is the exact target folder.
        """
        controller = ExportFilesController(
            ExportFilesControllerInput(
                config=self.config,
                local_folder_path=local_folder_path,
                cloud_provider_destination_path=cloud_provider_destination_path,
            )
        )
        response = await controller.execute()
        return response.__dict__
