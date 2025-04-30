from typing import Any, Dict

from .controllers.types.update_thies_data_types import UpdateThiesDataControllerInput
from .controllers.update_thies_data import UpdateThiesDataController
from saviialib.general_types.api.update_thies_data_types import (
    EpiiUpdateThiesConfig,
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
