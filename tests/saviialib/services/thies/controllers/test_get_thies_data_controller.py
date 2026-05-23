import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")
    setattr(pandas_stub, "DataFrame", type("DataFrame", (), {}))
    setattr(pandas_stub, "Series", type("Series", (), {}))
    setattr(pandas_stub, "read_csv", lambda *args, **kwargs: None)
    sys.modules["pandas"] = pandas_stub
if "numpy" not in sys.modules:
    sys.modules["numpy"] = types.ModuleType("numpy")

from saviialib.general_types.api.saviia_thies_api_types import SaviiaThiesConfig
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
)
from saviialib.general_types.error_types.common import (
    FtpClientError,
    SharepointClientError,
)
from saviialib.services.thies.controllers.get_thies_data import GetThiesDataController
from saviialib.services.thies.controllers.types.get_thies_data_types import (
    GetThiesDataControllerInput,
)
from saviialib.services.thies.use_cases.types.get_thies_data_types import (
    GetThiesDataUseCaseOutput,
)


class TestGetThiesDataControllerExecute(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = SaviiaThiesConfig(
            sharepoint_client_id="valid_client_id",
            sharepoint_client_secret="valid_client_secret",
            sharepoint_site_name="valid_site_name",
            sharepoint_tenant_id="valid_tenant_id",
            sharepoint_tenant_name="valid_tenant_name",
            local_backup_path="saviia-local-backup",
            logger=MagicMock(),
        )
        self.ftp_host = "localhost"
        self.ftp_port = 21
        self.ftp_user = "john_doe"
        self.ftp_password = "password"

    @patch("saviialib.services.thies.controllers.get_thies_data.GetThiesDataUseCase")
    async def test_should_return_all_success_messages(self, mock_use_case_class):
        scenarios = [
            (
                True,
                False,
                "Backup needed but no new data to sync to Microsoft SharePoint.",
            ),
            (False, True, "New data should be synced to Microsoft SharePoint."),
            (True, True, "New data synced to SharePoint and backup needed."),
            (False, False, "No new data to sync to Microsoft SharePoint."),
        ]

        for need_to_backup, need_to_sync, expected_message in scenarios:
            with self.subTest(need_to_backup=need_to_backup, need_to_sync=need_to_sync):
                mock_use_case_inst = mock_use_case_class.return_value
                mock_use_case_inst.execute = AsyncMock(
                    return_value=GetThiesDataUseCaseOutput(
                        need_to_backup=need_to_backup,
                        need_to_sync=need_to_sync,
                        unbacked_files=set(),
                        unsynchronised_files=set(),
                    )
                )
                controller = GetThiesDataController(
                    GetThiesDataControllerInput(
                        self.config,
                        self.ftp_host,
                        self.ftp_port,
                        self.ftp_user,
                        self.ftp_password,
                    )
                )
                result = await controller.execute()
                self.assertEqual(result.message, expected_message)
                self.assertEqual(result.status, 200)

    @patch("saviialib.services.thies.controllers.get_thies_data.GetThiesDataUseCase")
    async def test_should_handle_expected_errors(self, mock_use_case_class):
        scenarios = [
            (
                BackupSourcePathError(reason="missing"),
                "The specified local backup source path does not exist.",
                404,
            ),
            (
                FtpClientError("ftp"),
                "An error occurred while initializing FTP or SharePoint client.",
                500,
            ),
            (
                SharepointClientError("sharepoint"),
                "An error occurred while initializing FTP or SharePoint client.",
                500,
            ),
            (
                ValueError("boom"),
                "An unexpected error occurred during use case initialization.",
                400,
            ),
        ]

        for error, expected_message, expected_status in scenarios:
            with self.subTest(error=type(error).__name__):
                mock_use_case_inst = mock_use_case_class.return_value
                mock_use_case_inst.execute = AsyncMock(side_effect=error)
                controller = GetThiesDataController(
                    GetThiesDataControllerInput(
                        self.config,
                        self.ftp_host,
                        self.ftp_port,
                        self.ftp_user,
                        self.ftp_password,
                    )
                )
                result = await controller.execute()
                self.assertEqual(result.message, expected_message)
                self.assertEqual(result.status, expected_status)
                self.assertIn("error", result.metadata)

    async def test_should_reject_invalid_schema_input(self):
        controller = GetThiesDataController(
            GetThiesDataControllerInput(
                self.config,
                self.ftp_host,
                "21",
                self.ftp_user,
                self.ftp_password,
            )
        )

        result = await controller.execute()

        self.assertEqual(result.status, 400)
        self.assertEqual(result.message, "Invalid input data for getting THIES data.")
        self.assertIn("error", result.metadata)
