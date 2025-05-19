import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from saviialib.general_types.error_types.api.epii_api_error_types import (
    ThiesConnectionError,
    ThiesFetchingError,
)
from saviialib.services.epii.use_cases.types import (
    UpdateThiesDataUseCaseInput,
    FtpClientConfig,
    SharepointConfig,
)
from saviialib.services.epii.use_cases.update_thies_data import (
    UpdateThiesDataUseCase,
)


@pytest.mark.asyncio
@patch("saviialib.services.epii.use_cases.update_thies_data.FTPClient")
class TestUpdateThiesDataUseCaseFetchThiesFilenames(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ftp_config = FtpClientConfig(
            ftp_host="localhost",
            ftp_password="12345678",
            ftp_port=21,
            ftp_user="anonymous",
        )
        self.sharepoint_config = SharepointConfig(
            sharepoint_client_id="your_client_id",
            sharepoint_client_secret="your_client_secret",
            sharepoint_tenant_id="your_tenant_id",
            sharepoint_tenant_name="your_tenant_name",
            sharepoint_site_name="your_site_name",
        )
        self.sharepoint_folders_path = [
            "Shared%20Documents/General/Test_Raspberry/THIES/AVG",
            "Shared%20Documents/General/Test_Raspberry/THIES/EXT",
        ]
        self.ftp_server_folders_path = [
            "ftp/thies/BINFILES/ARCH_AV1",
            "ftp/thies/BINFILES/ARCH_EX1",
        ]

    async def test_should_fetch_thies_file_names_successfully(
        self, mock_ftp_client: MagicMock
    ):
        # Arrange
        use_case_input = UpdateThiesDataUseCaseInput(
            ftp_config=self.ftp_config,
            sharepoint_config=self.sharepoint_config,
            sharepoint_folders_path=self.sharepoint_folders_path,
            ftp_server_folders_path=self.ftp_server_folders_path,
        )
        use_case = UpdateThiesDataUseCase(use_case_input)
        expected_file_names = {
            "AVG_file1.bin",
            "AVG_file2.bin",
            "EXT_file1.bin",
            "EXT_file2.bin",
        }
        mock_ftp_client_inst = mock_ftp_client.return_value
        mock_ftp_client_inst.list_files = AsyncMock(
            side_effect=[
                ["file1.bin", "file2.bin"],  # AVG files
                ["file1.bin", "file2.bin"],  # EXT files
            ]
        )

        # Act
        file_names = await use_case.fetch_thies_file_names()

        # Assert
        self.assertEqual(file_names, expected_file_names)

    async def test_should_raise_connection_error(self, mock_ftp_client: MagicMock):
        # Arrange
        use_case_input = UpdateThiesDataUseCaseInput(
            ftp_config=self.ftp_config,
            sharepoint_config=self.sharepoint_config,
            sharepoint_folders_path=self.sharepoint_folders_path,
            ftp_server_folders_path=self.ftp_server_folders_path,
        )
        use_case = UpdateThiesDataUseCase(use_case_input)
        mock_ftp_client_inst = mock_ftp_client.return_value
        mock_ftp_client_inst.list_files = AsyncMock(
            side_effect=ConnectionRefusedError("Connection refused")
        )

        # Act & Assert
        with self.assertRaises(ThiesConnectionError) as context:
            await use_case.fetch_thies_file_names()
        self.assertEqual(str(context.exception.reason), "Connection refused")


@pytest.mark.asyncio
@patch("saviialib.services.epii.use_cases.update_thies_data.FTPClient")
class TestUpdateThiesDataUseCaseFetchThiesFileContent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ftp_config = FtpClientConfig(
            ftp_host="localhost",
            ftp_password="12345678",
            ftp_port=21,
            ftp_user="anonymous",
        )
        self.sharepoint_config = SharepointConfig(
            sharepoint_client_id="your_client_id",
            sharepoint_client_secret="your_client_secret",
            sharepoint_tenant_id="your_tenant_id",
            sharepoint_tenant_name="your_tenant_name",
            sharepoint_site_name="your_site_name",
        )
        self.sharepoint_folders_path = [
            "Shared%20Documents/General/Test_Raspberry/THIES/AVG",
            "Shared%20Documents/General/Test_Raspberry/THIES/EXT",
        ]
        self.ftp_server_folders_path = [
            "ftp/thies/BINFILES/ARCH_AV1",
            "ftp/thies/BINFILES/ARCH_EX1",
        ]

    async def test_should_fetch_thies_file_content_successfully(
        self, mock_ftp_client: MagicMock
    ):
        # Arrange
        use_case_input = UpdateThiesDataUseCaseInput(
            ftp_config=self.ftp_config,
            sharepoint_config=self.sharepoint_config,
            sharepoint_folders_path=self.sharepoint_folders_path,
            ftp_server_folders_path=self.ftp_server_folders_path,
        )
        use_case = UpdateThiesDataUseCase(use_case_input)
        use_case.uploading = {"AVG_file1.bin", "EXT_file2.bin"}
        mock_ftp_client_inst = mock_ftp_client.return_value
        mock_ftp_client_inst.read_file = AsyncMock(
            side_effect=lambda args: b"content_of_" + args.file_path.encode()
        )
        expected_content_files = {
            "AVG_file1.bin": b"content_of_ftp/thies/BINFILES/ARCH_AV1/file1.bin",
            "EXT_file2.bin": b"content_of_ftp/thies/BINFILES/ARCH_AV1/file2.bin",
        }

        # Act
        content_files = await use_case.fetch_thies_file_content()
        # Assert
        self.assertEqual(content_files, expected_content_files)

    async def test_should_raise_fetch_thies_file_content_error(
        self, mock_ftp_client: MagicMock
    ):
        # Arrange
        use_case_input = UpdateThiesDataUseCaseInput(
            ftp_config=self.ftp_config,
            sharepoint_config=self.sharepoint_config,
            sharepoint_folders_path=self.sharepoint_folders_path,
            ftp_server_folders_path=self.ftp_server_folders_path,
        )
        use_case = UpdateThiesDataUseCase(use_case_input)
        use_case.uploading = {"AVG_file1.bin"}
        mock_ftp_client_inst = mock_ftp_client.return_value
        mock_ftp_client_inst.read_file = AsyncMock(
            side_effect=ConnectionAbortedError("Failed to read file from FTP server")
        )

        # Act & Assert
        with self.assertRaises(ThiesFetchingError) as context:
            await use_case.fetch_thies_file_content()
        self.assertEqual(
            str(context.exception.reason), "Failed to read file from FTP server"
        )


@pytest.mark.asyncio
@patch("saviialib.services.epii.use_cases.update_thies_data.FTPClient")
@patch("saviialib.services.epii.use_cases.update_thies_data.SharepointClient")
class TestUpdateThiesDataUseCaseExecute(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ftp_config = FtpClientConfig(
            ftp_host="localhost",
            ftp_password="12345678",
            ftp_port=21,
            ftp_user="anonymous",
        )
        self.sharepoint_config = SharepointConfig(
            sharepoint_client_id="your_client_id",
            sharepoint_client_secret="your_client_secret",
            sharepoint_tenant_id="your_tenant_id",
            sharepoint_tenant_name="your_tenant_name",
            sharepoint_site_name="your_site_name",
        )
        self.sharepoint_folders_path = [
            "Shared%20Documents/General/Test_Raspberry/THIES/AVG",
            "Shared%20Documents/General/Test_Raspberry/THIES/EXT",
        ]
        self.ftp_server_folders_path = [
            "ftp/thies/BINFILES/ARCH_AV1",
            "ftp/thies/BINFILES/ARCH_EX1",
        ]

    async def test_should_execute_successfully(
        self, mock_sharepoint_client: MagicMock, mock_ftp_client: MagicMock
    ):
        # Arrange
        use_case_input = UpdateThiesDataUseCaseInput(
            ftp_config=self.ftp_config,
            sharepoint_config=self.sharepoint_config,
            sharepoint_folders_path=self.sharepoint_folders_path,
            ftp_server_folders_path=self.ftp_server_folders_path,
        )
        use_case = UpdateThiesDataUseCase(use_case_input)

        # Mocking methods used in execute
        use_case.fetch_thies_file_names = AsyncMock(
            return_value={"AVG_file1.bin", "EXT_file2.bin"}
        )
        use_case.fetch_cloud_file_names = AsyncMock(return_value={"AVG_file1.bin"})
        use_case.fetch_thies_file_content = AsyncMock(
            return_value={
                "EXT_file2.bin": b"content_of_ftp/thies/BINFILES/ARCH_EX1/file2.bin"
            }
        )
        use_case.upload_thies_files_to_sharepoint = AsyncMock(
            return_value={"EXT_file2.bin": "uploaded"}
        )

        # Act
        result = await use_case.execute()

        # Assert
        self.assertIsInstance(result, dict)
        self.assertIn("EXT_file2.bin", result)
        self.assertEqual(result["EXT_file2.bin"], "uploaded")

    # async def test_should_raise_empty_data_error(
    #     self, mock_sharepoint_client: MagicMock, mock_ftp_client: MagicMock
    # ):
    #     # Arrange
    #     use_case_input = UpdateThiesDataUseCaseInput(
    #         ftp_config=self.ftp_config,
    #         sharepoint_config=self.sharepoint_config,
    #         sharepoint_folders_path=self.sharepoint_folders_path,
    #         ftp_server_folders_path=self.ftp_server_folders_path,
    #     )
    #     use_case = UpdateThiesDataUseCase(use_case_input)
    #     mock_ftp_client_inst = mock_ftp_client.return_value
    #     mock_sharepoint_client_inst = mock_sharepoint_client.return_value

    #     mock_ftp_client_inst.list_files = AsyncMock(
    #         side_effect=[
    #             ["file1.bin"],  # AVG files
    #             ["file1.bin"],  # EXT files
    #         ]
    #     )
    #     mock_sharepoint_client_inst.list_files = AsyncMock(
    #         return_value={"value": [{"Name": "file1.bin"}]}
    #     )

    #     # Act & Assert
    #     with self.assertRaises(EmptyDataError) as context:
    #         await use_case.execute()
    #     self.assertEqual(str(context.exception.reason), "No files to upload.")
