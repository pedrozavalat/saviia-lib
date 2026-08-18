import unittest
import sys
import types
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

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
    ThiesFetchingError,
)

from saviialib.services.thies.use_cases.get_thies_data import GetThiesDataUseCase
from saviialib.services.thies.use_cases.types.get_thies_data_types import (
    GetThiesDataUseCaseInput,
)


class TestGetThiesDataUseCaseExecute(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.local_backup_path = self.tempdir.name
        self._ensure_local_backup_structure()
        self.ftp_client = MagicMock()
        self.ftp_client.list_files = AsyncMock()
        self.cloud_client = MagicMock()
        self.cloud_client.__aenter__ = AsyncMock(
            return_value=self.cloud_client
        )
        self.cloud_client.__aexit__ = AsyncMock(return_value=None)
        self.cloud_client.list_files = AsyncMock()
        self.files_client = MagicMock()
        self.directory_client = MagicMock()
        self.directory_client.join_paths.side_effect = lambda *paths: os.path.join(
            *paths
        )
        self.directory_client.path_exists = AsyncMock(return_value=True)
        self.directory_client.makedirs = AsyncMock()
        self.directory_client.listdir = AsyncMock(return_value=[])
        self.directory_client.isdir = AsyncMock(return_value=False)
        self.use_case = GetThiesDataUseCase(
            GetThiesDataUseCaseInput(
                ftp_client=self.ftp_client,
                cloud_client=self.cloud_client,
                files_client=self.files_client,
                directory_client=self.directory_client,
                local_backup_path=self.local_backup_path,
                cloud_provider_destination_path="/Volumes/catalog/schema/volume",
                logger=MagicMock(),
            )
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def _ensure_local_backup_structure(self):
        for folder in ("AVG", "EXT"):
            Path(self.local_backup_path, "thies", folder).mkdir(
                parents=True, exist_ok=True
            )

    def _build_use_case(self, need_to_sync: bool, need_to_backup: bool):
        return GetThiesDataUseCase(
            GetThiesDataUseCaseInput(
                ftp_client=self.ftp_client,
                cloud_client=self.cloud_client,
                files_client=self.files_client,
                directory_client=self.directory_client,
                local_backup_path=self.local_backup_path,
                cloud_provider_destination_path="/Volumes/catalog/schema/volume",
                logger=MagicMock(),
            )
        )

    async def test_should_detect_pending_backup_and_sync(self):
        self.use_case._fetch_local_backup_files = AsyncMock(
            return_value={
                "filenames": {"AVG_local.bin"},
                "count_avg_files": 1,
                "count_ext_files": 1,
            }
        )
        self.use_case._fetch_thies_total_files = AsyncMock(
            return_value={("AVG_local.bin", 100), ("EXT_remote.bin", 200)}
        )
        self.use_case._fetch_cloud_total_files = AsyncMock(
            return_value={("AVG_local.bin", 100)}
        )

        result = await self.use_case.execute()

        self.assertTrue(result.need_to_backup)
        self.assertTrue(result.need_to_sync)

    async def test_should_create_missing_backup_structure_and_list_files(self):
        self.directory_client.path_exists = AsyncMock(
            side_effect=[True, False, False, False]
        )
        self.directory_client.listdir = AsyncMock(
            side_effect=lambda path, more_info=False: os.listdir(path)
        )
        Path(self.local_backup_path, "thies", "AVG", "a.bin").write_bytes(b"a" * 11)
        Path(self.local_backup_path, "thies", "EXT", "b.bin").write_bytes(b"b" * 22)

        backup_files = await self.use_case._fetch_local_backup_files()

        self.assertEqual(backup_files["filenames"], {"AVG_a.bin", "EXT_b.bin"})
        self.assertEqual(backup_files["file_sizes"], {"AVG_a.bin": 11, "EXT_b.bin": 22})
        self.assertEqual(backup_files["count_avg_files"], 1)
        self.assertEqual(backup_files["count_ext_files"], 1)
        self.assertEqual(self.directory_client.makedirs.await_count, 3)

    async def test_should_mark_backup_needed_when_local_size_differs_from_ftp(self):
        use_case = self._build_use_case(need_to_sync=False, need_to_backup=False)

        result = use_case._validate_pending_files(
            {("AVG_20250201.BIN", 200)},
            set(),
            {
                "filenames": {"AVG_20250201.BIN"},
                "file_sizes": {"AVG_20250201.BIN": 100},
                "count_avg_files": 1,
                "count_ext_files": 1,
            },
        )

        self.assertTrue(result["need_to_backup"])

    async def test_should_raise_backup_source_path_error_when_backup_root_missing(self):
        self.directory_client.path_exists = AsyncMock(return_value=False)

        with self.assertRaises(BackupSourcePathError):
            await self.use_case._fetch_local_backup_files()

    async def test_should_raise_thies_fetching_error_when_ftp_list_fails(self):
        self.ftp_client.list_files = AsyncMock(
            side_effect=ConnectionRefusedError("connection refused")
        )

        with self.assertRaises(ThiesFetchingError):
            await self.use_case._fetch_thies_total_files()

    async def test_should_fetch_cloud_files_successfully(self):
        async def list_files(args):
            if args.folder_relative_url.endswith("/AVG"):
                return [
                    {"name": "avg.bin", "file_size": 10, "is_directory": False}
                ]
            return [{"name": "ext.bin", "file_size": 20, "is_directory": False}]

        self.cloud_client.list_files = AsyncMock(side_effect=list_files)

        cloud_files = await self.use_case._fetch_cloud_total_files()

        self.assertEqual(cloud_files, {("AVG_avg.bin", 10), ("EXT_ext.bin", 20)})

    async def test_should_execute_without_sync_when_cloud_fetch_fails(self):
        self.use_case._fetch_local_backup_files = AsyncMock(
            return_value={
                "filenames": {"AVG_local.bin"},
                "count_avg_files": 1,
                "count_ext_files": 1,
            }
        )
        self.use_case._fetch_thies_total_files = AsyncMock(
            return_value={("AVG_local.bin", 100), ("EXT_remote.bin", 200)}
        )
        self.use_case._fetch_cloud_total_files = AsyncMock(
            side_effect=RuntimeError("cloud provider down")
        )

        result = await self.use_case.execute()

        self.assertTrue(result.need_to_backup)
        self.assertFalse(result.need_to_sync)

    async def test_should_return_no_changes_when_cloud_and_backup_match(self):
        self.use_case._fetch_local_backup_files = AsyncMock(
            return_value={
                "filenames": {"AVG_local.bin", "EXT_remote.bin"},
                "count_avg_files": 1,
                "count_ext_files": 1,
            }
        )
        self.use_case._fetch_thies_total_files = AsyncMock(
            return_value={("AVG_local.bin", 100), ("EXT_remote.bin", 200)}
        )
        self.use_case._fetch_cloud_total_files = AsyncMock(
            return_value={("AVG_local.bin", 100), ("EXT_remote.bin", 200)}
        )

        result = await self.use_case.execute()

        self.assertFalse(result.need_to_backup)
        self.assertFalse(result.need_to_sync)
