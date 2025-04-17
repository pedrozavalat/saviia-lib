import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.rcer_iot_client_pkg.general_types.error_types.api.update_thies_data_error_types import (
    FetchThiesFileContentError,
    ThiesUploadEmptyError,
)
from src.rcer_iot_client_pkg.services.epii.use_cases.types import (
    UpdateThiesDataUseCaseInput,
)
from src.rcer_iot_client_pkg.services.epii.use_cases.update_thies_data import (
    UpdateThiesDataUseCase,
)


@pytest.mark.asyncio
@patch("src.rcer_iot_client_pkg.services.epii.use_cases.update_thies_data.FTPClient")
class TestUpdateThiesDataUseCaseFetchThiesFilenames(unittest.IsolatedAsyncioTestCase):
    async def test_should_fetch_thies_file_names_successfully(
        self, mock_ftp_client: MagicMock
    ):
        # Arrange
        use_case_input = UpdateThiesDataUseCaseInput(
            ftp_host="localhost",
            ftp_password="12345678",
            ftp_port=21,
            ftp_user="anonymous",
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
            return_value=["file1.bin", "file2.bin"]
        )

        # Act
        file_names = await use_case.fetch_thies_file_names()

        # Assert
        self.assertEqual(file_names, expected_file_names)

    async def test_should_raise_connection_error(self, mock_ftp_client: MagicMock):
        # Arrange
        use_case_input = UpdateThiesDataUseCaseInput(
            ftp_host="localhost",
            ftp_password="12345678",
            ftp_port=21,
            ftp_user="anonymous",
        )
        use_case = UpdateThiesDataUseCase(use_case_input)
        mock_ftp_client_inst = mock_ftp_client.return_value
        mock_ftp_client_inst.list_files = AsyncMock(
            side_effect=ConnectionError("No files were found to upload.")
        )

        # Act & Assert
        with self.assertRaises(ThiesUploadEmptyError) as context:
            await use_case.fetch_thies_file_names()
        self.assertEqual(str(context.exception), "No files were found to upload.")


@pytest.mark.asyncio
@patch("src.rcer_iot_client_pkg.services.epii.use_cases.update_thies_data.FTPClient")
class TestUpdateThiesDataUseCaseFetchThiesFileContent(unittest.IsolatedAsyncioTestCase):
    async def test_should_fetch_thies_file_content_successfully(
        self, mock_ftp_client: MagicMock
    ):
        # Arrange
        use_case_input = UpdateThiesDataUseCaseInput(
            ftp_host="localhost",
            ftp_password="12345678",
            ftp_port=21,
            ftp_user="anonymous",
        )
        use_case = UpdateThiesDataUseCase(use_case_input)
        use_case.uploading = ["AVG_file1.bin", "EXT_file2.bin"]
        mock_ftp_client_inst = mock_ftp_client.return_value
        mock_ftp_client_inst.read_file = AsyncMock(
            side_effect=lambda args: b"content_of_" + args.file_path.encode()
        )
        expected_content_files = {
            "file1.bin": b"content_of_ftp/thies/BINFILES/ARCH_AV1/file1.bin",
            "file2.bin": b"content_of_ftp/thies/BINFILES/ARCH_EX1/file2.bin",
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
            ftp_host="localhost",
            ftp_password="12345678",
            ftp_port=21,
            ftp_user="anonymous",
        )
        use_case = UpdateThiesDataUseCase(use_case_input)
        use_case.uploading = ["AVG_file1.bin"]
        mock_ftp_client_inst = mock_ftp_client.return_value
        mock_ftp_client_inst.read_file = AsyncMock(
            side_effect=ConnectionError("Failed to read file from FTP server")
        )

        # Act & Assert
        with self.assertRaises(FetchThiesFileContentError) as context:
            await use_case.fetch_thies_file_content()
        self.assertEqual(
            str(context.exception.args[0]), "Failed to read file from FTP server"
        )
