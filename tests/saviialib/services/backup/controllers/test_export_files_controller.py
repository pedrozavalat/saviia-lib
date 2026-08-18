import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")
    setattr(pandas_stub, "DataFrame", type("DataFrame", (), {}))
    setattr(pandas_stub, "Series", type("Series", (), {}))
    setattr(pandas_stub, "read_csv", lambda *args, **kwargs: None)
    sys.modules["pandas"] = pandas_stub
if "numpy" not in sys.modules:
    sys.modules["numpy"] = types.ModuleType("numpy")

from saviialib.general_types.api.saviia_backup_api_types import SaviiaBackupConfig
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
)
from saviialib.services.backup.controllers.export_files import ExportFilesController
from saviialib.services.backup.controllers.types.export_files_types import (
    ExportFilesControllerInput,
)
from saviialib.services.backup.use_cases.types.export_files_types import (
    ExportFilesUseCaseOutput,
)


@pytest.fixture
def backup_config() -> SaviiaBackupConfig:
    return SaviiaBackupConfig(
        client_name="databricks",
        databricks_api_key="token",
        databricks_host_url="https://workspace.azuredatabricks.net",
        logger=MagicMock(),
        local_backup_path="/tmp/backup",
    )


@pytest.mark.asyncio
@patch("saviialib.services.backup.controllers.export_files.SchemaValidatorClient")
@patch("saviialib.services.backup.controllers.export_files.ExportFilesUseCase")
@patch("saviialib.services.backup.controllers.export_files.DirectoryClient")
@patch("saviialib.services.backup.controllers.export_files.FilesClient")
@patch("saviialib.services.backup.controllers.export_files.CloudClient")
async def test_export_files_controller_should_return_success(
    mock_cloud_client_class,
    mock_files_client_class,
    mock_directory_client_class,
    mock_use_case_class,
    mock_schema_validator_class,
    backup_config,
):
    mock_schema_validator_class.return_value.validate.return_value = None
    mock_use_case = mock_use_case_class.return_value
    mock_use_case.execute = AsyncMock(
        return_value=ExportFilesUseCaseOutput(
            synced_files=["a.txt"],
            total_local_files=2,
            total_cloud_files=2,
            total_pending_files=1,
            total_synced_files=1,
        )
    )

    controller = ExportFilesController(
        ExportFilesControllerInput(
            config=backup_config,
            local_folder_path="thies-daily-files",
            cloud_provider_destination_path="/Volumes/catalog/schema/volume",
        )
    )
    result = await controller.execute()
    print(result)
    assert result.status == 200
    assert result.message == "Folder files exported successfully."
    assert result.metadata["data"]["synced_files"] == ["a.txt"]
    assert mock_cloud_client_class.called
    assert mock_files_client_class.called
    assert mock_directory_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.backup.controllers.export_files.SchemaValidatorClient")
@patch("saviialib.services.backup.controllers.export_files.ExportFilesUseCase")
@patch("saviialib.services.backup.controllers.export_files.DirectoryClient")
@patch("saviialib.services.backup.controllers.export_files.FilesClient")
@patch("saviialib.services.backup.controllers.export_files.CloudClient")
async def test_export_files_controller_should_handle_invalid_path(
    mock_cloud_client_class,
    mock_files_client_class,
    mock_directory_client_class,
    mock_use_case_class,
    mock_schema_validator_class,
    backup_config,
):
    mock_schema_validator_class.return_value.validate.return_value = None
    mock_use_case = mock_use_case_class.return_value
    mock_use_case.execute = AsyncMock(
        side_effect=BackupSourcePathError(reason="missing path")
    )

    controller = ExportFilesController(
        ExportFilesControllerInput(
            config=backup_config,
            local_folder_path="thies-daily-files",
            cloud_provider_destination_path="/Volumes/catalog/schema/volume",
        )
    )
    result = await controller.execute()

    assert result.status == 400
    assert result.message == "Invalid local backup path or folder."
    assert "error" in result.metadata
    assert mock_cloud_client_class.called
    assert mock_files_client_class.called
    assert mock_directory_client_class.called
