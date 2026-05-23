import unittest
import sys
import types
from unittest.mock import AsyncMock, MagicMock

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
    ThiesFetchingError,
)

if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")
    setattr(pandas_stub, "DataFrame", type("DataFrame", (), {}))
    setattr(pandas_stub, "Series", type("Series", (), {}))
    setattr(pandas_stub, "read_csv", lambda *args, **kwargs: None)
    sys.modules["pandas"] = pandas_stub
if "numpy" not in sys.modules:
    sys.modules["numpy"] = types.ModuleType("numpy")

from saviialib.services.thies.use_cases.get_thies_data import GetThiesDataUseCase
from saviialib.services.thies.use_cases.types.get_thies_data_types import (
    GetThiesDataUseCaseInput,
)


class TestGetThiesDataUseCaseExecute(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ftp_client = MagicMock()
        self.ftp_client.list_files = AsyncMock()
        self.sharepoint_client = MagicMock()
        self.sharepoint_client.site_name = "site_name_123"
        self.sharepoint_client.__aenter__ = AsyncMock(return_value=self.sharepoint_client)
        self.sharepoint_client.__aexit__ = AsyncMock(return_value=None)
        self.sharepoint_client.list_files = AsyncMock()
        self.files_client = MagicMock()
        self.directory_client = MagicMock()
        self.directory_client.path_exists = AsyncMock(return_value=True)
        self.directory_client.makedirs = AsyncMock()
        self.directory_client.listdir = AsyncMock(return_value=[])
        self.use_case = GetThiesDataUseCase(
            GetThiesDataUseCaseInput(
                ftp_client=self.ftp_client,
                sharepoint_client=self.sharepoint_client,
                files_client=self.files_client,
                directory_client=self.directory_client,
                local_backup_path="/tmp/saviia-local-backup",
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
        self.assertIn("EXT_remote.bin", result.unbacked_files)
        self.assertIn("EXT_remote.bin", result.unsynchronised_files)

    async def test_should_create_missing_backup_structure_and_list_files(self):
        self.directory_client.path_exists = AsyncMock(side_effect=[True, False, False, False])
        self.directory_client.listdir = AsyncMock(side_effect=[["AVG_a.bin"], ["EXT_b.bin"]])

        backup_files = await self.use_case._fetch_local_backup_files()

        self.assertEqual(backup_files["filenames"], {"AVG_a.bin"})
        self.assertEqual(backup_files["count_avg_files"], 1)
        self.assertEqual(backup_files["count_ext_files"], 1)
        self.assertEqual(self.directory_client.makedirs.await_count, 3)

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
                return {"value": [{"Name": "avg.bin", "Length": "10"}]}
            return {"value": [{"Name": "ext.bin", "Length": "20"}]}

        self.sharepoint_client.list_files = AsyncMock(side_effect=list_files)

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
            side_effect=RuntimeError("sharepoint down")
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
