from typing import Any, Dict

from .controllers.types.update_thies_data_types import UpdateThiesDataControllerInput
from .controllers.types.upload_backup_to_sharepoint_types import (
    UploadBackupToSharepointControllerInput,
)
from .controllers.update_thies_data import UpdateThiesDataController
from .controllers.upload_backup_to_sharepoint import UploadBackupToSharepointController
from saviialib.general_types.api.epii_api_types import (
    EpiiUpdateThiesConfig,
    EpiiSharepointBackupConfig,
)


class EpiiAPI:
    """
    EpiiAPI is a service class that provides methods to interact with Patagonia Center system.
    """

    async def update_thies_data(self, config: EpiiUpdateThiesConfig) -> Dict[str, Any]:
        """
        This method establishes a connection to an FTP server using the provided
        credentials and updates data related to THIES Data Logger.
        Args:
            config (EpiiUpdateThiesConfig): configuration class for FTP Server and Microsoft SharePoint credentials.
        Returns:
            response (dict): A dictionary representation of the API response.
        """
        controller = UpdateThiesDataController(UpdateThiesDataControllerInput(config))
        response = await controller.execute()
        return response.__dict__

    async def upload_backup_to_sharepoint(
        self, config: EpiiSharepointBackupConfig
    ) -> Dict[str, Any]:
        """Migrate a backup folder from Home assistant to Sharepoint directory.
        Args:
            config (EpiiUpdateThiesConfig): Configuration object containing the necessary
                information for the upload, such as the SharePoint directory and the
                backup source path.
        Returns:
            response (dict): A dictionary containing the response from the upload operation.
                This dictionary will typically include information about the success or
                failure of the upload, as well as any relevant metadata.
        """

        controller = UploadBackupToSharepointController(
            UploadBackupToSharepointControllerInput(config)
        )
        response = await controller.execute()
        return response.__dict__
