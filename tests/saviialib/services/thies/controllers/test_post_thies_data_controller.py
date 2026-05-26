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
    SharePointDirectoryError,
    SharePointFetchingError,
    SharePointUploadError,
    ThiesConnectionError,
    ThiesFetchingError,
)
from saviialib.general_types.error_types.common import (
    EmptyDataError,
    FtpClientError,
    SharepointClientError,
)
from saviialib.services.thies.controllers.post_thies_data import PostThiesDataController
from saviialib.services.thies.controllers.types.post_thies_data_types import (
    PostThiesDataControllerInput,
)


class TestPostThiesDataControllerExecute(unittest.IsolatedAsyncioTestCase):
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
        self.sharepoint_destination_path = "Shared%20Documents/General/Test_Raspberry"
        self.ftp_server_folders_path = [
            "ftp/thies/BINFILES/ARCH_AV1",
            "ftp/thies/BINFILES/ARCH_EX1",
        ]
        self.local_backup_source_path = "saviia-local-backup"

    @patch("saviialib.services.thies.controllers.post_thies_data.PostThiesDataUseCase")
    async def test_should_return_all_success_messages(self, mock_use_case_class):
        scenarios = [
            (True, True, "THIES data was backed up and synced successfully"),
            (True, False, "THIES backup was processed successfully"),
            (False, True, "THIES data was synced successfully"),
            (False, False, "No operation was requested"),
        ]

        for need_to_backup, need_to_sync, expected_message in scenarios:
            with self.subTest(need_to_backup=need_to_backup, need_to_sync=need_to_sync):
                mock_use_case_inst = mock_use_case_class.return_value
                mock_use_case_inst.need_to_backup = need_to_backup
                mock_use_case_inst.need_to_sync = need_to_sync
                mock_use_case_inst.execute = AsyncMock(return_value={"data": "value"})
                controller = PostThiesDataController(
                    PostThiesDataControllerInput(
                        self.config,
                        self.ftp_host,
                        self.ftp_port,
                        self.ftp_user,
                        self.ftp_password,
                        need_to_sync,
                        need_to_backup,
                        self.sharepoint_destination_path,
                        self.ftp_server_folders_path,
                        self.local_backup_source_path,
                    )
                )
                result = await controller.execute()
                self.assertEqual(result.message, expected_message)
                self.assertEqual(result.status, 200)

    @patch("saviialib.services.thies.controllers.post_thies_data.PostThiesDataUseCase")
    async def test_should_handle_expected_errors(self, mock_use_case_class):
        scenarios = [
            (EmptyDataError(reason="empty"), "No files to upload", 204),
            (
                BackupSourcePathError(reason="missing"),
                "The specified local backup source path does not exist.",
                404,
            ),
            (FtpClientError("ftp"), "Ftp Client initialization fails.", 400),
            (
                SharepointClientError("sharepoint"),
                "Sharepoint Client initialization fails.",
                500,
            ),
            (
                SharePointFetchingError(
                    reason=Exception('fetch,{"error_description": "fetch"}')
                ),
                "An error occurred while retrieving file names from Microsoft SharePoint",
                400,
            ),
            (
                SharePointUploadError(reason="upload"),
                "An error ocurred while uploading files to RCER Cloud",
                400,
            ),
            (
                SharePointDirectoryError(reason="dir"),
                "An error ocurred while extracting folders from Microsoft Sharepoint",
                400,
            ),
            (
                ThiesFetchingError(reason="thies"),
                "An error ocurred while retrieving file names from THIES FTP Server.",
                204,
            ),
            (
                ThiesConnectionError(reason="conn"),
                "Unable to connect to THIES Data Logger FTP Server.",
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
                controller = PostThiesDataController(
                    PostThiesDataControllerInput(
                        self.config,
                        self.ftp_host,
                        self.ftp_port,
                        self.ftp_user,
                        self.ftp_password,
                        True,
                        True,
                        self.sharepoint_destination_path,
                        self.ftp_server_folders_path,
                        self.local_backup_source_path,
                    )
                )
                result = await controller.execute()
                self.assertEqual(result.message, expected_message)
                self.assertEqual(result.status, expected_status)
                if not isinstance(error, EmptyDataError):
                    self.assertIn("error", result.metadata)

    async def test_should_reject_invalid_schema_input(self):
        controller = PostThiesDataController(
            PostThiesDataControllerInput(
                self.config,
                self.ftp_host,
                self.ftp_port,
                self.ftp_user,
                self.ftp_password,
                "yes",
                True,
                self.sharepoint_destination_path,
                self.ftp_server_folders_path,
                self.local_backup_source_path,
            )
        )

        result = await controller.execute()

        self.assertEqual(result.status, 400)
        self.assertEqual(result.message, "Invalid input data for posting THIES data.")
        self.assertIn("error", result.metadata)
