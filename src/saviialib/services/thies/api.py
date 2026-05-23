from typing import Any, Dict, List
from saviialib.general_types.api.saviia_thies_api_types import (
    SaviiaThiesConfig,
)
from .controllers import (
    UpdateThiesDataControllerInput,
    UpdateThiesDataController,
    DetectFailuresController,
    DetectFailuresControllerInput,
    GetThiesDataController,
    GetThiesDataControllerInput,
    PostThiesDataController,
    PostThiesDataControllerInput,
)
from saviialib.libs.log_client import (
    LogClient,
    LogClientArgs,
    LogStatus,
    DebugArgs,
)


class SaviiaThiesAPI:
    def __init__(self, config: SaviiaThiesConfig) -> None:
        self.config = config
        self.logger = LogClient(
            LogClientArgs("logging", service_name="thies", class_name="api")
        )

    async def get_thies_data(
        self,
        ftp_port: int,
        ftp_host: str,
        ftp_user: str,
        ftp_password: str,
        sharepoint_destination_path: str,
    ):
        """Get the status of synchronization and backup needs for a THIES Data Logger.
        :param ftp_host: FTP server hostname or IP address where the THIES Data Logger data is stored.
        :param ftp_port: FTP server port number where the THIES Data Logger data is stored.
        :param ftp_user: FTP server username for authentication to access the THIES Data Logger data.
        :param ftp_password: FTP server password for authentication to access the THIES Data Logger data.

        :return: A dictionary representation of the API response, where status indicators included are:
            `need_to_sync`, whether new data needs to be synchronized to SharePoint;
            `need_to_backup`, whether a backup is needed for the local data.
        :rtype: dict"""
        controller = GetThiesDataController(
            GetThiesDataControllerInput(
                self.config,
                ftp_host,
                ftp_port,
                ftp_user,
                ftp_password,
                sharepoint_destination_path,
            )
        )
        response = await controller.execute()
        return response.__dict__

    async def update_thies_data(
        self,
        ftp_port: int,
        ftp_host: str,
        ftp_user: str,
        ftp_password: str,
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
                ftp_host,
                ftp_port,
                ftp_user,
                ftp_password,
                sharepoint_folders_path,
                ftp_server_folders_path,
                local_backup_source_path,
            )
        )
        response = await controller.execute()
        return response.__dict__

    async def post_thies_data(
        self,
        ftp_port: int,
        ftp_host: str,
        ftp_user: str,
        ftp_password: str,
        need_to_sync: bool,
        need_to_backup: bool,
        sharepoint_destination_path: str,
        ftp_server_folders_path: List[str],
        local_backup_source_path: str,
    ) -> Dict[str, Any]:
        """Execute THIES backup and/or synchronisation using a precomputed status.

        :param bool need_to_sync: Whether the local backup must be synchronized to SharePoint.
        :param bool need_to_backup: Whether the THIES FTP server must be backed up locally.
        :param str sharepoint_destination_path: Shared SharePoint folder path where THIES data will be stored.
        :param ftp_host: FTP server hostname or IP address where the THIES Data Logger data is stored.
        :param ftp_port: FTP server port number where the THIES Data Logger data is stored.
        :param ftp_user: FTP server username for authentication to access the THIES Data Logger data.
        :param ftp_password: FTP server password for authentication to access the THIES Data Logger data.
        :param list ftp_server_folders_path: FTP server folder paths for AVG and EXT data.
            The AVG path must be the first element.
        :param str local_backup_source_path: Path of the main directory where the files extracted from
            the Thies FTP Server are stored.

        :return: A dictionary representation of the API response.
        :rtype: dict
        """
        self.logger.method_name = "post_thies_data"
        self.logger.debug(
            DebugArgs(
                status=LogStatus.STARTED,
                metadata={
                    "msg": f"need_to_backup={need_to_backup}, need_to_sync={need_to_sync}"
                },
            )
        )
        controller = PostThiesDataController(
            PostThiesDataControllerInput(
                self.config,
                ftp_host,
                ftp_port,
                ftp_user,
                ftp_password,
                need_to_sync,
                need_to_backup,
                sharepoint_destination_path,
                ftp_server_folders_path,
                local_backup_source_path,
            )
        )
        response = await controller.execute()
        self.logger.debug(
            DebugArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={"msg": f"status={response.status}"},
            )
        )
        return response.__dict__

    async def detect_failures(
        self,
        local_backup_source_path: str,
        n_days: int = 7,
        db_driver: str = "",
        db_host: str = "",
        db_name: str = "",
        user: str = "",
        pwd: str = "",
    ) -> Dict[str, Any]:
        controller = DetectFailuresController(
            DetectFailuresControllerInput(
                self.config,
                local_backup_source_path,
                n_days,
                db_driver,
                db_host,
                db_name,
                user,
                pwd,
            )
        )
        response = await controller.execute()
        return response.__dict__
