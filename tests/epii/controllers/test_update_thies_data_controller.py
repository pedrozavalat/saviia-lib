import unittest
from unittest.mock import AsyncMock, patch

from rcer_iot_client_pkg.general_types.error_types.api.update_thies_data_error_types import (
    SharePointFetchingError,
)
from rcer_iot_client_pkg.general_types.error_types.common import (
    FtpClientError,
    SharepointClientError,
    EmptyDataError,
)
from rcer_iot_client_pkg.services.epii.controllers.types import (
    UpdateThiesDataControllerInput,
)
from rcer_iot_client_pkg.services.epii.controllers.update_thies_data import (
    UpdateThiesDataController,
)


class TestUpdateThiesDataControllerExecute(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.host = "localhost"
        self.port = 8080
        self.user = "admin"
        self.password = "password"

    @patch(
        "rcer_iot_client_pkg.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_execute_successfully(self, mock_use_case_class):
        mock_use_case_inst = mock_use_case_class.return_value
        mock_use_case_inst.execute = AsyncMock(return_value={"key": "value"})

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                ftp_host=self.host,
                ftp_port=self.port,
                ftp_user=self.user,
                ftp_password=self.password,
            )
        )

        result = await controller.execute()

        self.assertEqual(result.message, "THIES was synced successfully")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.metadata["data"], {"key": "value"})

    @patch(
        "rcer_iot_client_pkg.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_handle_ftp_client_error(self, mock_use_case):
        mock_use_case_inst = mock_use_case.return_value
        mock_use_case_inst.execute.side_effect = FtpClientError("FTP")

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                ftp_host=self.host,
                ftp_port=self.port,
                ftp_user=self.user,
                ftp_password=self.password,
            )
        )

        result = await controller.execute()

        self.assertEqual(result.message, "Ftp Client initialization fails.")
        self.assertEqual(result.status, 400)
        self.assertIn("Ftp Client", result.metadata["error"])

    @patch(
        "rcer_iot_client_pkg.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_handle_sharepoint_client_error(self, mock_use_case):
        mock_use_case_inst = mock_use_case.return_value
        mock_use_case_inst.execute.side_effect = SharepointClientError("Sharepoint")

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                ftp_host=self.host,
                ftp_port=self.port,
                ftp_user=self.user,
                ftp_password=self.password,
            )
        )

        result = await controller.execute()

        self.assertEqual(result.message, "Sharepoint Client initialization fails.")
        self.assertEqual(result.status, 400)
        self.assertIn("SharePoint", result.metadata["error"])

    @patch(
        "rcer_iot_client_pkg.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_handle_sharepoint_fetching_error(self, mock_use_case):
        mock_use_case_inst = mock_use_case.return_value
        mock_use_case_inst.execute.side_effect = SharePointFetchingError("Fetch error")

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                ftp_host=self.host,
                ftp_port=self.port,
                ftp_user=self.user,
                ftp_password=self.password,
            )
        )

        result = await controller.execute()

        self.assertEqual(
            result.message,
            "An error occurred while retrieving file names from the RCER cloud",
        )
        self.assertEqual(result.status, 500)
        self.assertIn("RCER cloud", result.metadata["error"])

    @patch(
        "rcer_iot_client_pkg.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_handle_thies_data_empty_empty_error(self, mock_use_case):
        mock_use_case_inst = mock_use_case.return_value
        mock_use_case_inst.execute.side_effect = EmptyDataError(reason="No files")

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                ftp_host=self.host,
                ftp_port=self.port,
                ftp_user=self.user,
                ftp_password=self.password,
            )
        )

        result = await controller.execute()

        self.assertEqual(result.message, "No files to upload")
        self.assertEqual(result.status, 204)

    @patch(
        "rcer_iot_client_pkg.services.epii.controllers.update_thies_data.UpdateThiesDataUseCase"
    )
    async def test_should_handle_unexpected_error(self, mock_use_case):
        mock_use_case_inst = mock_use_case.return_value
        mock_use_case_inst.execute.side_effect = ValueError("Unexpected error")

        controller = UpdateThiesDataController(
            UpdateThiesDataControllerInput(
                ftp_host=self.host,
                ftp_port=self.port,
                ftp_user=self.user,
                ftp_password=self.password,
            )
        )

        result = await controller.execute()

        self.assertEqual(
            result.message,
            "An unexpected error occurred during use case initialization.",
        )
        self.assertEqual(result.status, 400)
        self.assertIn("Unexpected error", result.metadata["error"])
