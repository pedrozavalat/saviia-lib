from typing import Any, Dict, List

from .controllers.types.update_thies_data_types import UpdateThiesDataControllerInput
from .controllers.update_thies_data import UpdateThiesDataController
from saviialib.general_types.api.saviia_thies_api_types import (
    SaviiaThiesConfig,
)


class SaviiaThiesAPI:
    def __init__(self, config: SaviiaThiesConfig) -> None:
        self.config = config

    async def update_thies_data(
        self,
        sharepoint_folders_path: List[str],
        ftp_server_folders_path: List[str],
        local_backup_source_path: str,
    ) -> Dict[str, Any]:
        """Updates data from a THIES Data Logger by connecting to an FTP server
        and transferring data to specified Sharepoint folders.

        :param list sharepoint_folders_path: List of Sharepoint folder paths for AVG and EXT data.
            The AVG path must be the first element.
        :param list ftp_server_folders_path: List of FTP server folder paths for AVG and EXT data.
            The AVG path must be the first element.
        :param str local_backup_source_path: Path of the main directory where the files extracted from
            the Thies FTP Server are going to be stored

        :return: A dictionary representation of the API response.
        :rtype: dict
        """
        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                self.config,
                sharepoint_folders_path,
                ftp_server_folders_path,
                local_backup_source_path,
            )
        )
        response = await controller.execute()
        return response.__dict__