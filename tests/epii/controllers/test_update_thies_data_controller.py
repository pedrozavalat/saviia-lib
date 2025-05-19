import unittest
from unittest.mock import AsyncMock, patch

from saviialib.general_types.error_types.api.epii_api_error_types import (
    SharePointFetchingError,
)
from saviialib.general_types.error_types.common import (
    FtpClientError,
    SharepointClientError,
    EmptyDataError,
)
from saviialib.services.epii.controllers.types import (
    UpdateThiesDataControllerInput,
)
from saviialib.services.epii.controllers.update_thies_data import (
    UpdateThiesDataController,
)
from saviialib.general_types.api.epii_api_types import (
    EpiiUpdateThiesConfig,
)


class TestUpdateThiesDataControllerExecute(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = EpiiUpdateThiesConfig(
            ftp_host="localhost",
            ftp_port=21,
            ftp_user="john_doe",
            ftp_password="password",
            sharepoint_client_id="valid_client_id",
            sharepoint_client_secret="valid_client_secret",
            sharepoint_site_name="valid_site_name",
            sharepoint_tenant_id="valid_tenant_id",
            sharepoint_tenant_name="valid_tenant_name",
        )
        self.sharepoint_folders_path = [
            "Shared%20Documents/General/Test_Raspberry/THIES/AVG",
            "Shared%20Documents/General/Test_Raspberry/THIES/EXT",
        ]
        self.ftp_server_folders_path = [
            "ftp/thies/BINFILES/ARCH_AV1",
            "ftp/thies/BINFILES/ARCH_EX1",
        ]

    @patch(
        "saviialib.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_execute_successfully(self, mock_use_case_class):
        mock_use_case_inst = mock_use_case_class.return_value
        mock_use_case_inst.execute = AsyncMock(return_value={"key": "value"})

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                self.config, self.sharepoint_folders_path, self.ftp_server_folders_path
            )
        )

        result = await controller.execute()

        self.assertEqual(result.message, "THIES was synced successfully")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.metadata["data"], {"key": "value"})

    @patch(
        "saviialib.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_handle_ftp_client_error(self, mock_use_case):
        mock_use_case_inst = mock_use_case.return_value
        mock_use_case_inst.execute.side_effect = FtpClientError("FTP")

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                self.config, self.sharepoint_folders_path, self.ftp_server_folders_path
            )
        )

        result = await controller.execute()

        self.assertEqual(result.message, "Ftp Client initialization fails.")
        self.assertEqual(result.status, 400)
        self.assertIn("Ftp Client", result.metadata["error"])

    @patch(
        "saviialib.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_handle_sharepoint_client_error(self, mock_use_case):
        mock_use_case_inst = mock_use_case.return_value
        mock_use_case_inst.execute.side_effect = SharepointClientError("Sharepoint")

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                self.config, self.sharepoint_folders_path, self.ftp_server_folders_path
            )
        )

        result = await controller.execute()

        self.assertEqual(result.message, "Sharepoint Client initialization fails.")
        self.assertEqual(result.status, 500)
        self.assertIn("SharePoint", result.metadata["error"])

    @patch(
        "saviialib.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_handle_sharepoint_fetching_error(self, mock_use_case):
        mock_use_case_inst = mock_use_case.return_value
        mock_use_case_inst.execute.side_effect = SharePointFetchingError(
            reason="any, {error: error}"
        )

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                self.config, self.sharepoint_folders_path, self.ftp_server_folders_path
            )
        )

        result = await controller.execute()

        self.assertEqual(
            result.message,
            "An error occurred while retrieving file names from Microsoft SharePoint",
        )
        self.assertEqual(result.status, 400)

    @patch(
        "saviialib.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_handle_thies_data_empty_empty_error(self, mock_use_case):
        mock_use_case_inst = mock_use_case.return_value
        mock_use_case_inst.execute.side_effect = EmptyDataError(reason="No files")

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                self.config, self.sharepoint_folders_path, self.ftp_server_folders_path
            )
        )

        result = await controller.execute()

        self.assertEqual(result.message, "No files to upload")
        self.assertEqual(result.status, 204)

    @patch(
        "saviialib.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_handle_unexpected_error(self, mock_use_case):
        mock_use_case_inst = mock_use_case.return_value
        mock_use_case_inst.execute.side_effect = ValueError("Unexpected error")

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                self.config, self.sharepoint_folders_path, self.ftp_server_folders_path
            )
        )

        result = await controller.execute()

        self.assertEqual(
            result.message,
            "An unexpected error occurred during use case initialization.",
        )
        self.assertEqual(result.status, 400)
        self.assertIn("Unexpected error", result.metadata["error"])
