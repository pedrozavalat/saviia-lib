from typing import Dict, Any

from .controllers.types.update_thies_data_types import UpdateThiesDataControllerInput
from .controllers.update_thies_data import UpdateThiesDataController


class EpiiAPI:
    """
    EpiiAPI is a service class that provides methods to interact with Patagonia Center system.
    """

    async def update_thies_data(
        self,
        ftp_port: int,
        ftp_host: str,
        ftp_password: str,
        ftp_user: str,
    ) -> Dict[str, Any]:
        """
        This method establishes a connection to an FTP server using the provided
        credentials and updates data related to THIES Data Logger.
        Args:
            ftp_port (int): The port number of the FTP server.
            ftp_host (str): The hostname or IP address of the FTP server.
            ftp_password (str): The password for the FTP server.
            ftp_user (str): The username for the FTP server.
        Returns:
            response (dict): A dictionary representation of the API response.
        """
        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                ftp_port=ftp_port,
                ftp_host=ftp_host,
                ftp_password=ftp_password,
                ftp_user=ftp_user,
            )
        )
        response = await controller.execute()
        return response.__dict__
