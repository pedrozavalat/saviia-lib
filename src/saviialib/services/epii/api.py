from typing import Any, Dict, List

from .controllers.types.update_thies_data_types import UpdateThiesDataControllerInput
from .controllers.types.upload_backup_to_sharepoint_types import (
    UploadBackupToSharepointControllerInput,
)
from .controllers.update_thies_data import UpdateThiesDataController
from .controllers.upload_backup_to_sharepoint import UploadBackupToSharepointController
from saviialib.general_types.api.epii_api_types import (
    EpiiUpdateThiesConfig,
    EpiiSharepointBackupConfig,
    EpiiAPIConfig,
)


class EpiiAPI:
    """
    EpiiAPI is a service class that provides methods to interact with Patagonia Center system.
    """

    def __init__(self, config: EpiiAPIConfig):
        self.ftp_port = config.ftp_port
        self.ftp_host = config.ftp_host
        self.ftp_user = config.ftp_user
        self.ftp_password = config.ftp_password
        self.sharepoint_client_id = config.sharepoint_client_id
        self.sharepoint_client_secret = config.sharepoint_client_secret
        self.sharepoint_tenant_id = config.sharepoint_tenant_id
        self.sharepoint_tenant_name = config.sharepoint_tenant_name
        self.sharepoint_site_name = config.sharepoint_site_name
        self.logger = config.logger

    async def update_thies_data(
        self, sharepoint_folders_path: List[str], ftp_server_folders_path: List[str]
    ) -> Dict[str, Any]:
        """Updates data from a THIES Data Logger by connecting to an FTP server
        and transferring data to specified Sharepoint folders.

        Args:
            sharepoint_folders_path (list): List of Sharepoint folder paths for AVG and EXT data.
            The AVG path must be the first element.
            ftp_server_folders_path (list): List of FTP server folder paths for AVG and EXT data.
            The AVG path must be the first element.

        Returns:
            dict: A dictionary representation of the API response.
        """
        config = EpiiUpdateThiesConfig(
            ftp_port=self.ftp_port,
            ftp_host=self.ftp_host,
            ftp_user=self.ftp_user,
            ftp_password=self.ftp_password,
            sharepoint_client_id=self.sharepoint_client_id,
            sharepoint_client_secret=self.sharepoint_client_secret,
            sharepoint_site_name=self.sharepoint_site_name,
            sharepoint_tenant_id=self.sharepoint_tenant_id,
            sharepoint_tenant_name=self.sharepoint_tenant_name,
            logger=self.logger,
        )
        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                config, sharepoint_folders_path, ftp_server_folders_path
            )
        )
        response = await controller.execute()
        return response.__dict__

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
        config = EpiiSharepointBackupConfig(
            sharepoint_client_id=self.sharepoint_client_id,
            sharepoint_client_secret=self.sharepoint_client_secret,
            sharepoint_site_name=self.sharepoint_site_name,
            sharepoint_tenant_id=self.sharepoint_tenant_id,
            sharepoint_tenant_name=self.sharepoint_tenant_name,
            logger=self.logger,
        )

        controller = UploadBackupToSharepointController(
            UploadBackupToSharepointControllerInput(
                config, local_backup_source_path, sharepoint_destination_path
            )
        )
        response = await controller.execute()
        return response.__dict__
