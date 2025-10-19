from .controllers.get_miniseed_files import (
    GetMiniseedFilesController,
    GetMiniseedFilesControllerInput,
)
from saviialib.general_types.api.saviia_shakes_api_types import SaviiaShakesConfig

from typing import Dict


class ShakesAPI:
    """This class provides methods for interacting with Raspberry Shakes"""

    def __init__(self, config: SaviiaShakesConfig) -> None:
        self.config = config

    async def get_miniseed_files(self, raspberry_shakes: Dict[str, str]):
        """Download the MiniSEED files from the SFTP Server provided by each Raspberry Shake.
        Args:
            raspberry_shakes (dict): Dictionary where the key is the name of the Raspberry Shake,
                and the value is the IP Address.
        Returns:
            response (dict): A dictionary containg the response from the download operation.
                This response will tipically include the message, the response status, and metadata.
        """
        controller = GetMiniseedFilesController(
            GetMiniseedFilesControllerInput(
                config=self.config, raspberry_shakes=raspberry_shakes
            )
        )
        response = await controller.execute()
        return response.__dict__
