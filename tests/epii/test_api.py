import unittest
from unittest.mock import Mock, patch

from rcer_iot_client_pkg.services.epii.api import EpiiAPI
from rcer_iot_client_pkg.services.epii.controllers.types import (
    UpdateThiesDataControllerOutput,
)


class TestEpiiAPIUpdateThiesData(unittest.TestCase):
    @patch("rcer_iot_client_pkg.services.epii.api.UpdateThiesDataController")
    def test_should_update_thies_data_successfully(
        self, mock_update_thies_data_controller: Mock
    ):
        # Arrange
        api = EpiiAPI()
        ftp_port = 21
        ftp_host = "ftp.example.com"
        ftp_password = "password123"
        ftp_user = "user123"
        expected_response = UpdateThiesDataControllerOutput(
            message="valid message", status=200, metadata={"data": "value"}
        )
        mock_update_thies_data_controller_inst = (
            mock_update_thies_data_controller.return_value
        )
        mock_update_thies_data_controller_inst.execute.return_value = expected_response
        # Act
        response = api.update_thies_data(
            ftp_port=ftp_port,
            ftp_host=ftp_host,
            ftp_password=ftp_password,
            ftp_user=ftp_user,
        )
        # Assert
        self.assertEqual(response, expected_response.__dict__)
        mock_update_thies_data_controller_inst.execute.assert_called_once()
