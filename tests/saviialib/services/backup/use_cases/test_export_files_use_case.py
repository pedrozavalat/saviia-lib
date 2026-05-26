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

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
)
from saviialib.services.backup.use_cases.export_files import ExportFilesUseCase
from saviialib.services.backup.use_cases.types.export_files_types import (
    ExportFilesUseCaseInput,
)


@pytest.fixture
def use_case_input() -> ExportFilesUseCaseInput:
    sharepoint_client = MagicMock()
    sharepoint_client.site_name = "uc365_CentrosyEstacionesRegionalesUC"
    sharepoint_client.__aenter__ = AsyncMock(return_value=sharepoint_client)
    sharepoint_client.__aexit__ = AsyncMock(return_value=None)
    sharepoint_client.create_folder = AsyncMock(return_value={})
    sharepoint_client.list_files = AsyncMock(
        return_value={
            "value": [
                {"Name": "a.txt", "Length": "10"},
                {"Name": "b.txt", "Length": "99"},
            ]
        }
    )
    sharepoint_client.upload_file = AsyncMock(return_value={})

    directory_client = MagicMock()
    directory_client.join_paths.side_effect = lambda *paths: "/".join(paths)
    directory_client.path_exists = AsyncMock(side_effect=[True, True])
    directory_client.isdir = AsyncMock(side_effect=[True, False, False])
    directory_client.listdir = AsyncMock(return_value=[("a.txt", 10), ("b.txt", 20)])

    files_client = MagicMock()
    files_client.read = AsyncMock(return_value=b"data")

    return ExportFilesUseCaseInput(
        sharepoint_client=sharepoint_client,
        files_client=files_client,
        directory_client=directory_client,
        local_backup_path="/tmp/backup",
        local_folder_path="daily-files",
        sharepoint_destination_path="Shared%20Documents/General/Test/daily-files",
        logger=MagicMock(),
    )


@pytest.mark.asyncio
@patch("saviialib.services.backup.use_cases.export_files.LogClient")
async def test_export_files_use_case_should_sync_only_pending_files(
    mock_log_client_class,
    use_case_input,
):
    use_case = ExportFilesUseCase(use_case_input)
    result = await use_case.execute()

    assert result.total_local_files == 2
    assert result.total_pending_files == 1
    assert result.total_synced_files == 1
    assert result.synced_files == ["b.txt"]
    use_case_input.sharepoint_client.upload_file.assert_awaited_once()
    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.backup.use_cases.export_files.LogClient")
async def test_export_files_use_case_should_reject_subfolders(
    mock_log_client_class,
    use_case_input,
):
    use_case_input.directory_client.path_exists = AsyncMock(side_effect=[True, True])
    use_case_input.directory_client.isdir = AsyncMock(side_effect=[True, True])
    use_case_input.directory_client.listdir = AsyncMock(return_value=[("nested", 0)])

    use_case = ExportFilesUseCase(use_case_input)
    with pytest.raises(ValueError, match="files only"):
        await use_case.execute()

    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.backup.use_cases.export_files.LogClient")
async def test_export_files_use_case_should_fail_when_backup_path_is_missing(
    mock_log_client_class,
    use_case_input,
):
    use_case_input.directory_client.path_exists = AsyncMock(return_value=False)

    use_case = ExportFilesUseCase(use_case_input)
    with pytest.raises(BackupSourcePathError):
        await use_case.execute()

    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.backup.use_cases.export_files.LogClient")
async def test_export_files_use_case_should_prefix_sharepoint_site_base_url(
    mock_log_client_class,
    use_case_input,
):
    use_case = ExportFilesUseCase(use_case_input)
    result = await use_case.execute()

    assert result.total_synced_files == 1
    create_folder_arg = (
        use_case_input.sharepoint_client.create_folder.await_args_list[0]
        .args[0]
        .folder_relative_url
    )
    upload_arg = (
        use_case_input.sharepoint_client.upload_file.await_args_list[0]
        .args[0]
        .folder_relative_url
    )
    assert create_folder_arg.startswith("/sites/uc365_CentrosyEstacionesRegionalesUC/")
    assert upload_arg.startswith("/sites/uc365_CentrosyEstacionesRegionalesUC/")
    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.backup.use_cases.export_files.LogClient")
async def test_export_files_use_case_should_sync_only_missing_file(
    mock_log_client_class,
    use_case_input,
):
    use_case_input.directory_client.listdir = AsyncMock(
        return_value=[(".PASS.txt", 10), ("tasks.xlsx", 200), ("20260331_tasks.xlsx", 300)]
    )
    use_case_input.directory_client.path_exists = AsyncMock(side_effect=[True, True])
    use_case_input.directory_client.isdir = AsyncMock(
        side_effect=[True, False, False, False]
    )
    use_case_input.sharepoint_client.list_files = AsyncMock(
        return_value={
            "value": [
                {"Name": ".PASS.txt", "Length": "10"},
                {"Name": "tasks.xlsx", "Length": "200"},
            ]
        }
    )
    use_case_input.sharepoint_client.upload_file = AsyncMock(return_value={})

    use_case = ExportFilesUseCase(use_case_input)
    result = await use_case.execute()

    assert result.total_local_files == 3
    assert result.total_cloud_files == 2
    assert result.total_pending_files == 1
    assert result.total_synced_files == 1
    assert result.synced_files == ["20260331_tasks.xlsx"]
    use_case_input.sharepoint_client.upload_file.assert_awaited_once()
    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.backup.use_cases.export_files.LogClient")
async def test_export_files_use_case_should_not_resync_when_cloud_size_is_unknown_zero(
    mock_log_client_class,
    use_case_input,
):
    use_case_input.directory_client.listdir = AsyncMock(
        return_value=[(".PASS.txt", 10), ("tasks.xlsx", 200), ("20260331_tasks.xlsx", 300)]
    )
    use_case_input.directory_client.path_exists = AsyncMock(side_effect=[True, True])
    use_case_input.directory_client.isdir = AsyncMock(
        side_effect=[True, False, False, False]
    )
    use_case_input.sharepoint_client.list_files = AsyncMock(
        return_value={
            "value": [
                {"Name": ".PASS.txt", "Length": "0"},
                {"Name": "tasks.xlsx", "Length": "0"},
                {"Name": "20260331_tasks.xlsx", "Length": "0"},
            ]
        }
    )
    use_case_input.sharepoint_client.upload_file = AsyncMock(return_value={})

    use_case = ExportFilesUseCase(use_case_input)
    result = await use_case.execute()

    assert result.total_local_files == 3
    assert result.total_cloud_files == 3
    assert result.total_pending_files == 0
    assert result.total_synced_files == 0
    assert result.synced_files == []
    use_case_input.sharepoint_client.upload_file.assert_not_called()
    assert mock_log_client_class.called
