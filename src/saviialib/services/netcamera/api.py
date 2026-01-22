from .controllers.get_camera_rates import (
    GetCameraRatesController,
    GetCameraRatesControllerInput,
)
from typing import Dict, Any
from saviialib.general_types.api.saviia_netcamera_api_types import SaviiaNetcameraConfig


class SaviiaNetcameraAPI:
    """This class provides methods for interacting with network cameras"""

    def __init__(self, config: SaviiaNetcameraConfig):
        self.config = config

    async def get_camera_rates(
        self, latitude: float, longitude: float
    ) -> Dict[str, Any]:
        """Returns the records a photos rates for any network camera installed at the station.

        The capturation is defined using meteorologic metrics from OpenMeteo Client,
        and they are: precipitation and precipitation probability.

        Args:
            - latitude (float): The latitude of the station location.
            - longitude (float): The longitude of the station location.

        Returns:
            dict: A dictionary containing the camera rates information.
        """
        controller = GetCameraRatesController(
            GetCameraRatesControllerInput(self.config, latitude, longitude)
        )
        response = await controller.execute()
        return response.__dict__
