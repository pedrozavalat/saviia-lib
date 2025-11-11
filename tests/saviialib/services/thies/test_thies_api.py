from saviialib import SaviiaAPI, SaviiaAPIConfig
import unittest
from unittest.mock import AsyncMock, patch, Mock
from saviialib.services.thies.controllers.update_thies_data import (
    UpdateThiesDataControllerOutput,
)


class TestEpiiAPIUpdateThiesData(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = SaviiaAPIConfig(
            ftp_host="ftp.example.com",
            ftp_port=21,
            ftp_password="password123",
            ftp_user="user123",
            sharepoint_client_id="client_id_123",
            sharepoint_client_secret="client_secret_123",
            sharepoint_site_name="site_name_123",
            sharepoint_tenant_id="tenant_id_123",
            sharepoint_tenant_name="tenant_name_123",
            logger=Mock(),
        )
        self.sharepoint_folders_path = [
            "Shared%20Documents/General/Test_Raspberry/THIES/AVG",
            "Shared%20Documents/General/Test_Raspberry/THIES/EXT",
        ]
        self.ftp_server_folders_path = [
            "ftp/thies/BINFILES/ARCH_AV1",
            "ftp/thies/BINFILES/ARCH_EX1",
        ]
        self.local_backup_source_path = "saviia-lib-backup"
        self.thies_service = SaviiaAPI(self.config).get("thies")

    @patch("saviialib.services.thies.api.UpdateThiesDataController")
    async def test_should_update_thies_data_successfully(
        self, mock_update_thies_data_controller
    ):
        # Arrange
        expected_response = UpdateThiesDataControllerOutput(
            message="valid message", status=200, metadata={"data": "value"}
        )

        mock_update_thies_data_controller_inst = (
            mock_update_thies_data_controller.return_value
        )
        mock_update_thies_data_controller_inst.execute = AsyncMock(
            return_value=expected_response
        )

        # Act
        response = await self.thies_service.update_thies_data(
            sharepoint_folders_path=self.sharepoint_folders_path,
            ftp_server_folders_path=self.ftp_server_folders_path,
            local_backup_source_path=self.local_backup_source_path
        )

        # Assert
        self.assertEqual(response, expected_response.__dict__)
        mock_update_thies_data_controller_inst.execute.assert_called_once()
