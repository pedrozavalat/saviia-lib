from .controllers.get_media_files import (
    GetMediaFilesController,
    GetMediaFilesControllerInput,
)
from typing import Dict, Tuple, Any
from saviialib.general_types.api.saviia_netcamera_api_types import SaviiaNetcameraConfig


class NetcameraAPI:
    """This class provides methods for interacting with network cameras and retrieving
    files using streaming services."""

    def __init__(self, config: SaviiaNetcameraConfig):
        self.config = config

    async def get_media_files(
        self, cameras: Dict[str, Tuple[str, int]]
    ) -> Dict[str, Any]:
        """Retrieve media files from Network cameras.

        :param cameras: Dictionary where the key is the identifier of the camera, and the
            value is a tuple wich contains the service IP address and port of connection.
            Example: {'cam_01': ('192.168.1.10', 8080), ...}
        :type cameras: dict
        :return response: A dictionary containg information of the extraction operation.
        :rtype: dict
        """
        controller = GetMediaFilesController(GetMediaFilesControllerInput(cameras))
        response = await controller.execute()
        return response.__dict__
