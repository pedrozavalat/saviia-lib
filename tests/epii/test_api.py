import unittest
from unittest.mock import AsyncMock, patch, Mock

from dotenv import load_dotenv

from saviialib.services.epii.api import EpiiAPI, EpiiAPIConfig
from saviialib.services.epii.controllers.types import (
    UpdateThiesDataControllerOutput,
)

load_dotenv()


class TestEpiiAPIUpdateThiesData(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = EpiiAPIConfig(
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

    @patch("saviialib.services.epii.api.UpdateThiesDataController")
    async def test_should_update_thies_data_successfully(
        self, mock_update_thies_data_controller
    ):
        # Arrange
        api = EpiiAPI(self.config)
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
        response = await api.update_thies_data()

        # Assert
        self.assertEqual(response, expected_response.__dict__)
        mock_update_thies_data_controller_inst.execute.assert_called_once()
