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
from saviialib.services.backup.use_cases.types.upload_backup_to_sharepoint_types import (
    UploadBackupToSharepointUseCaseInput,
)
from saviialib.services.backup.use_cases.upload_backup_to_sharepoint import (
    UploadBackupToSharepointUsecase,
)


@pytest.fixture
def backup_config() -> SaviiaBackupConfig:
    return SaviiaBackupConfig(
        sharepoint_client_id="client-id",
        sharepoint_client_secret="client-secret",
        sharepoint_tenant_id="tenant-id",
        sharepoint_tenant_name="tenant-name",
        sharepoint_site_name="site-name",
        logger=MagicMock(),
        local_backup_path="/tmp/backup",
    )


@pytest.mark.asyncio
@patch("saviialib.services.backup.use_cases.upload_backup_to_sharepoint.LogClient")
@patch(
    "saviialib.services.backup.use_cases.upload_backup_to_sharepoint.SharepointClient"
)
@patch(
    "saviialib.services.backup.use_cases.upload_backup_to_sharepoint.DirectoryClient"
)
@patch("saviialib.services.backup.use_cases.upload_backup_to_sharepoint.FilesClient")
@patch(
    "saviialib.services.backup.use_cases.upload_backup_to_sharepoint.calculate_percentage_uploaded",
    return_value=100.0,
)
@patch(
    "saviialib.services.backup.use_cases.upload_backup_to_sharepoint.parse_execute_response",
    return_value={"new_files": 1},
)
@patch("saviialib.services.backup.use_cases.upload_backup_to_sharepoint.save_file")
async def test_backup_use_case_should_orchestrate_the_upload_flow(
    mock_save_file,
    mock_parse_execute_response,
    mock_calculate_percentage_uploaded,
    mock_files_client_class,
    mock_directory_client_class,
    mock_sharepoint_client_class,
    mock_log_client_class,
    backup_config,
):
    mock_sharepoint_client = mock_sharepoint_client_class.return_value
    mock_sharepoint_client.__aenter__ = AsyncMock(return_value=mock_sharepoint_client)
    mock_sharepoint_client.__aexit__ = AsyncMock(return_value=None)
    mock_sharepoint_client.create_folder = AsyncMock(return_value=None)

    use_case = UploadBackupToSharepointUsecase(
        UploadBackupToSharepointUseCaseInput(
            sharepoint_config=backup_config,
            local_backup_source_path="/tmp/local",
            sharepoint_destination_path="Shared%20Documents/backup",
            logger=MagicMock(),
        )
    )
    use_case.prepare_backup = AsyncMock(return_value=None)
    use_case.migrate_files = AsyncMock(return_value=[])

    result = await use_case.execute()

    assert result == {"new_files": 1}
    use_case.prepare_backup.assert_awaited_once()
    use_case.migrate_files.assert_awaited_once()
    mock_calculate_percentage_uploaded.assert_called_once()
    mock_parse_execute_response.assert_called_once()
    assert mock_save_file.await_count == 2
    assert mock_log_client_class.called
    assert mock_files_client_class.called
    assert mock_directory_client_class.called
