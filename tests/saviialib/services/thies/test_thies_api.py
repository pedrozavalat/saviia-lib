import sys
import types
import unittest
from unittest.mock import AsyncMock, patch, Mock

if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")
    setattr(pandas_stub, "DataFrame", type("DataFrame", (), {}))
    setattr(pandas_stub, "Series", type("Series", (), {}))
    setattr(pandas_stub, "read_csv", lambda *args, **kwargs: None)
    sys.modules["pandas"] = pandas_stub
if "numpy" not in sys.modules:
    sys.modules["numpy"] = types.ModuleType("numpy")

from saviialib import SaviiaAPI, SaviiaAPIConfig
from saviialib.services.thies.controllers.get_thies_data import (
    GetThiesDataControllerOutput,
)
from saviialib.services.thies.controllers.post_thies_data import (
    PostThiesDataControllerOutput,
)
from saviialib.services.thies.controllers.detect_failures import (
    DetectFailuresControllerOutput,
)
from saviialib.services.thies.controllers.update_thies_data import (
    UpdateThiesDataControllerOutput,
)


class TestEpiiAPIUpdateThiesData(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ftp_host = "ftp.example.com"
        self.ftp_port = 21
        self.ftp_password = "password123"
        self.ftp_user = "user123"
        self.config = SaviiaAPIConfig(
            sharepoint_client_id="client_id_123",
            sharepoint_client_secret="client_secret_123",
            sharepoint_site_name="site_name_123",
            sharepoint_tenant_id="tenant_id_123",
            sharepoint_tenant_name="tenant_name_123",
            logger=Mock(),
            local_backup_path="/share/G",
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
            ftp_port=self.ftp_port,
            ftp_host=self.ftp_host,
            ftp_user=self.ftp_user,
            ftp_password=self.ftp_password,
            sharepoint_folders_path=self.sharepoint_folders_path,
            ftp_server_folders_path=self.ftp_server_folders_path,
            local_backup_source_path=self.local_backup_source_path,
        )

        # Assert
        self.assertEqual(response, expected_response.__dict__)
        mock_update_thies_data_controller_inst.execute.assert_called_once()

    @patch("saviialib.services.thies.api.GetThiesDataController")
    async def test_should_get_thies_data_successfully(
        self, mock_get_thies_data_controller
    ):
        expected_response = GetThiesDataControllerOutput(
            message="valid message",
            status=200,
            metadata={"data": "need_to_backup=True, need_to_sync=True"},
        )
        mock_get_thies_data_controller_inst = (
            mock_get_thies_data_controller.return_value
        )
        mock_get_thies_data_controller_inst.execute = AsyncMock(
            return_value=expected_response
        )

        response = await self.thies_service.get_thies_data(
            ftp_port=self.ftp_port,
            ftp_host=self.ftp_host,
            ftp_user=self.ftp_user,
            ftp_password=self.ftp_password,
            sharepoint_destination_path="Shared%20Documents/General/Test_Raspberry",
        )

        self.assertEqual(response, expected_response.__dict__)
        mock_get_thies_data_controller_inst.execute.assert_called_once()

    @patch("saviialib.services.thies.api.PostThiesDataController")
    async def test_should_post_thies_data_successfully(
        self, mock_post_thies_data_controller
    ):
        expected_response = PostThiesDataControllerOutput(
            message="valid message",
            status=200,
            metadata={"data": "backup={}, sync={}"},
        )
        mock_post_thies_data_controller_inst = (
            mock_post_thies_data_controller.return_value
        )
        mock_post_thies_data_controller_inst.execute = AsyncMock(
            return_value=expected_response
        )

        response = await self.thies_service.post_thies_data(
            ftp_port=self.ftp_port,
            ftp_host=self.ftp_host,
            ftp_user=self.ftp_user,
            ftp_password=self.ftp_password,
            need_to_sync=True,
            need_to_backup=True,
            sharepoint_destination_path="Shared%20Documents/General/Test_Raspberry",
            ftp_server_folders_path=self.ftp_server_folders_path,
            local_backup_source_path=self.local_backup_source_path,
        )

        self.assertEqual(response, expected_response.__dict__)
        mock_post_thies_data_controller_inst.execute.assert_called_once()

    @patch("saviialib.services.thies.api.DetectFailuresController")
    async def test_should_detect_failures_successfully(
        self, mock_detect_failures_controller
    ):
        expected_response = DetectFailuresControllerOutput(
            message="valid message",
            status=200,
            metadata={"validation": "ok"},
        )
        mock_detect_failures_controller_inst = (
            mock_detect_failures_controller.return_value
        )
        mock_detect_failures_controller_inst.execute = AsyncMock(
            return_value=expected_response
        )

        response = await self.thies_service.detect_failures(
            local_backup_source_path=self.local_backup_source_path,
            n_days=7,
            db_driver="odbc",
            db_host="localhost",
            db_name="thies",
            user="user",
            pwd="pwd",
        )

        self.assertEqual(response, expected_response.__dict__)
        mock_detect_failures_controller_inst.execute.assert_called_once()
