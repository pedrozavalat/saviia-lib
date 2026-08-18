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
    cloud_client = MagicMock()
    cloud_client.client_name = "databricks"
    cloud_client.__aenter__ = AsyncMock(return_value=cloud_client)
    cloud_client.__aexit__ = AsyncMock(return_value=None)
    cloud_client.resolve_url.side_effect = lambda args: args.folder_path.rstrip("/")
    cloud_client.create_folder = AsyncMock(return_value={})
    cloud_client.list_files = AsyncMock(
        return_value=[
            {"name": "a.txt", "file_size": 10, "is_directory": False},
            {"name": "b.txt", "file_size": 99, "is_directory": False},
        ]
    )
    cloud_client.upload_file = AsyncMock(return_value={})

    directory_client = MagicMock()
    directory_client.join_paths.side_effect = lambda *paths: "/".join(paths)
    directory_client.path_exists = AsyncMock(side_effect=[True, True])
    directory_client.isdir = AsyncMock(side_effect=[True, False, False])
    directory_client.listdir = AsyncMock(return_value=[("a.txt", 10), ("b.txt", 20)])

    files_client = MagicMock()
    files_client.read = AsyncMock(return_value=b"data")

    return ExportFilesUseCaseInput(
        cloud_client=cloud_client,
        files_client=files_client,
        directory_client=directory_client,
        local_backup_path="/tmp/backup",
        local_folder_path="daily-files",
        cloud_provider_destination_path="/Volumes/catalog/schema/volume",
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
    use_case_input.cloud_client.upload_file.assert_awaited_once()
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
async def test_export_files_use_case_should_preserve_databricks_volume_path(
    mock_log_client_class,
    use_case_input,
):
    use_case = ExportFilesUseCase(use_case_input)
    result = await use_case.execute()

    assert result.total_synced_files == 1
    create_folder_arg = (
        use_case_input.cloud_client.create_folder.await_args_list[0]
        .args[0]
        .folder_relative_url
    )
    upload_arg = (
        use_case_input.cloud_client.upload_file.await_args_list[0]
        .args[0]
        .folder_relative_url
    )
    assert create_folder_arg.startswith("/Volumes/catalog/schema/volume/")
    assert upload_arg.startswith("/Volumes/catalog/schema/volume/")
    assert "https://" not in create_folder_arg
    assert "https://" not in upload_arg
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
    use_case_input.cloud_client.list_files = AsyncMock(
        return_value=[
            {"name": ".PASS.txt", "file_size": 10, "is_directory": False},
            {"name": "tasks.xlsx", "file_size": 200, "is_directory": False},
        ]
    )
    use_case_input.cloud_client.upload_file = AsyncMock(return_value={})

    use_case = ExportFilesUseCase(use_case_input)
    result = await use_case.execute()

    assert result.total_local_files == 3
    assert result.total_cloud_files == 2
    assert result.total_pending_files == 1
    assert result.total_synced_files == 1
    assert result.synced_files == ["20260331_tasks.xlsx"]
    use_case_input.cloud_client.upload_file.assert_awaited_once()
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
    use_case_input.cloud_client.list_files = AsyncMock(
        return_value=[
            {"name": ".PASS.txt", "file_size": 0, "is_directory": False},
            {"name": "tasks.xlsx", "file_size": 0, "is_directory": False},
            {
                "name": "20260331_tasks.xlsx",
                "file_size": 0,
                "is_directory": False,
            },
        ]
    )
    use_case_input.cloud_client.upload_file = AsyncMock(return_value={})

    use_case = ExportFilesUseCase(use_case_input)
    result = await use_case.execute()

    assert result.total_local_files == 3
    assert result.total_cloud_files == 3
    assert result.total_pending_files == 0
    assert result.total_synced_files == 0
    assert result.synced_files == []
    use_case_input.cloud_client.upload_file.assert_not_called()
    assert mock_log_client_class.called
