import tempfile
import unittest
import os
import sys
import types
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
    CloudClientFetchingError,
    CloudClientUploadError,
    ThiesConnectionError,
)
from saviialib.general_types.error_types.common import EmptyDataError

from saviialib.services.thies.use_cases.post_thies_data import PostThiesDataUseCase
from saviialib.services.thies.use_cases.types.post_thies_data_types import (
    PostThiesDataUseCaseInput,
)


class TestPostThiesDataUseCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.local_backup_path = self.tempdir.name
        self._ensure_local_backup_structure()
        self.directory_client = MagicMock()
        self.directory_client.join_paths.side_effect = lambda *paths: os.path.join(
            *paths
        )
        self.directory_client.path_exists = AsyncMock(return_value=True)
        self.directory_client.makedirs = AsyncMock()
        self.directory_client.listdir = AsyncMock(side_effect=self._fake_listdir)
        self.directory_client.isdir = AsyncMock(return_value=False)
        self.files_client = MagicMock()
        self.files_client.read = AsyncMock()
        self.files_client.write = AsyncMock(side_effect=self._fake_write)
        self.ftp_client = MagicMock()
        self.ftp_client.list_files = AsyncMock()
        self.ftp_client.read_file = AsyncMock(side_effect=self._fake_ftp_read_file)
        self.cloud_client = MagicMock()
        self.cloud_client.__aenter__ = AsyncMock(
            return_value=self.cloud_client
        )
        self.cloud_client.__aexit__ = AsyncMock(return_value=None)
        self.cloud_client.create_folder = AsyncMock(return_value=None)
        self.cloud_client.list_files = AsyncMock()
        self.cloud_client.upload_file = AsyncMock(return_value={})

    def tearDown(self):
        self.tempdir.cleanup()

    def _ensure_local_backup_structure(self):
        for folder in ("AVG", "EXT"):
            Path(self.local_backup_path, "thies", folder).mkdir(
                parents=True, exist_ok=True
            )

    async def _fake_ftp_read_file(self, args):
        return f"content:{args.file_path}".encode()

    async def _fake_listdir(self, path, more_info=False):
        entries = []
        for name in os.listdir(path):
            full_path = Path(path, name)
            if more_info:
                entries.append(
                    (name, full_path.stat().st_size if full_path.is_file() else 0)
                )
            else:
                entries.append(name)
        return entries

    async def _fake_write(self, args):
        destination = Path(args.destination_path)
        destination.mkdir(parents=True, exist_ok=True)
        (destination / args.file_name).write_bytes(args.file_content)

    def _build_use_case(self, need_to_sync: bool, need_to_backup: bool):
        return PostThiesDataUseCase(
            PostThiesDataUseCaseInput(
                ftp_client=self.ftp_client,
                cloud_client=self.cloud_client,
                files_client=self.files_client,
                directory_client=self.directory_client,
                cloud_provider_destination_path="/Volumes/catalog/schema/volume",
                ftp_server_folders_path=[
                    "ftp://192.168.1.200:21/ARCH_AV1",
                    "ftp://192.168.1.200:21/ARCH_EX1",
                ],
                local_backup_source_path=self.local_backup_path,
                need_to_sync=need_to_sync,
                need_to_backup=need_to_backup,
                logger=MagicMock(),
            )
        )

    async def test_should_fill_local_backup_from_ftp(self):
        use_case = self._build_use_case(need_to_sync=False, need_to_backup=True)

        saved_files = await use_case._fill_local_backup(
            {
                ("AVG_sensor_a.BIN", 10),
                ("EXT_sensor_b.BIN", 20),
            }
        )

        self.assertEqual(saved_files, {"AVG_sensor_a.BIN", "EXT_sensor_b.BIN"})
        self.assertEqual(self.ftp_client.read_file.await_count, 2)
        self.assertTrue(
            Path(self.local_backup_path, "thies", "AVG", "sensor_a.BIN").exists()
        )
        self.assertTrue(
            Path(self.local_backup_path, "thies", "EXT", "sensor_b.BIN").exists()
        )

    async def test_should_create_thies_cloud_folders(self):
        use_case = self._build_use_case(need_to_sync=True, need_to_backup=False)

        await use_case._validate_cloud_destination()

        folder_urls = [
            call.args[0].folder_relative_url
            for call in self.cloud_client.create_folder.await_args_list
        ]
        cloud_thies_path = (
            "/Volumes/catalog/schema/volume/"
            f"{Path(self.local_backup_path).name}/thies"
        )
        self.assertCountEqual(
            folder_urls,
            [
                cloud_thies_path,
                f"{cloud_thies_path}/AVG",
                f"{cloud_thies_path}/EXT",
            ],
        )

    async def test_should_upload_files_to_cloud_inside_thies_destination(self):
        use_case = self._build_use_case(need_to_sync=True, need_to_backup=False)

        await use_case.upload_thies_files_to_cloud(
            {
                "AVG_sensor_a.BIN": b"content-a",
                "EXT_sensor_b.BIN": b"content-b",
            }
        )

        upload_urls = [
            call.args[0].folder_relative_url
            for call in self.cloud_client.upload_file.await_args_list
        ]
        cloud_thies_path = (
            "/Volumes/catalog/schema/volume/"
            f"{Path(self.local_backup_path).name}/thies"
        )
        self.assertEqual(
            upload_urls,
            [
                f"{cloud_thies_path}/AVG",
                f"{cloud_thies_path}/EXT",
            ],
        )

    async def test_should_raise_empty_data_error_when_no_operation_requested(self):
        use_case = self._build_use_case(need_to_sync=False, need_to_backup=False)

        with self.assertRaises(EmptyDataError):
            await use_case.execute()

    async def test_should_validate_local_backup_and_create_missing_dirs(self):
        self.directory_client.path_exists = AsyncMock(side_effect=[False, False, False])
        use_case = self._build_use_case(need_to_sync=False, need_to_backup=False)

        await use_case._validate_local_backup()

        self.assertEqual(self.directory_client.makedirs.await_count, 3)

    async def test_should_raise_thies_fetching_error_when_ftp_list_fails(self):
        self.ftp_client.list_files = AsyncMock(
            side_effect=ConnectionRefusedError("connection refused")
        )
        use_case = self._build_use_case(need_to_sync=False, need_to_backup=True)

        with self.assertRaises(ThiesConnectionError):
            await use_case.fetch_thies_file_names()

    async def test_should_fetch_cloud_files_successfully(self):
        async def list_files(args):
            if args.folder_relative_url.endswith("/AVG"):
                return [
                    {"name": "avg.bin", "file_size": 10, "is_directory": False}
                ]
            return [{"name": "ext.bin", "file_size": 20, "is_directory": False}]

        self.cloud_client.list_files = AsyncMock(side_effect=list_files)
        use_case = self._build_use_case(need_to_sync=True, need_to_backup=False)

        cloud_files = await use_case.fetch_cloud_file_names()

        self.assertEqual(cloud_files, {("AVG_avg.bin", 10), ("EXT_ext.bin", 20)})

    async def test_should_raise_cloud_fetching_error_when_list_fails(self):
        self.cloud_client.list_files = AsyncMock(side_effect=RuntimeError("boom"))
        use_case = self._build_use_case(need_to_sync=True, need_to_backup=False)

        with self.assertRaises(CloudClientFetchingError):
            await use_case.fetch_cloud_file_names()

    async def test_should_fetch_local_backup_file_names(self):
        use_case = self._build_use_case(need_to_sync=True, need_to_backup=False)
        self.directory_client.listdir = AsyncMock(
            side_effect=[[("a.bin", 0)], [("b.bin", 0)]]
        )

        files = await use_case.fetch_local_backup_file_names()

        self.assertEqual(files, {("AVG_a.bin", 0), ("EXT_b.bin", 0)})

    async def test_should_fetch_local_backup_file_content(self):
        use_case = self._build_use_case(need_to_sync=True, need_to_backup=False)
        use_case.uploading = {"AVG_sensor_a.BIN", "EXT_sensor_b.BIN"}

        async def read(args):
            if args.file_path.endswith("/AVG/sensor_a.BIN"):
                return b"content-a"
            return b"content-b"

        self.files_client.read = AsyncMock(side_effect=read)

        content_files = await use_case.fetch_local_backup_file_content()

        self.assertEqual(
            content_files,
            {"AVG_sensor_a.BIN": b"content-a", "EXT_sensor_b.BIN": b"content-b"},
        )

    async def test_should_raise_cloud_upload_error_when_upload_fails(self):
        self.cloud_client.upload_file = AsyncMock(
            side_effect=ConnectionError("cloud upload failed")
        )
        use_case = self._build_use_case(need_to_sync=True, need_to_backup=False)

        with self.assertRaises(CloudClientUploadError):
            await use_case.upload_thies_files_to_cloud(
                {"AVG_sensor_a.BIN": b"content-a"}
            )

    async def test_should_raise_backup_source_path_error_when_validation_fails(self):
        self.directory_client.path_exists = AsyncMock(side_effect=OSError("boom"))
        use_case = self._build_use_case(need_to_sync=False, need_to_backup=True)

        with self.assertRaises(BackupSourcePathError):
            await use_case.execute()

    async def test_should_sync_pending_files_only_when_needed(self):
        use_case = self._build_use_case(need_to_sync=True, need_to_backup=False)

        pending = await use_case._sync_pending_files(
            {("AVG_sensor_a.BIN", 10), ("EXT_sensor_b.BIN", 20)},
            {("AVG_sensor_a.BIN", 10)},
        )

        self.assertEqual(pending, {"EXT_sensor_b.BIN"})

    async def test_should_skip_daily_statistics_when_file_missing(self):
        use_case = self._build_use_case(need_to_sync=False, need_to_backup=True)
        self.directory_client.listdir = AsyncMock(return_value=["OTHER.BIN"])

        await use_case._extract_thies_daily_statistics()

    async def test_should_execute_backup_only(self):
        use_case = self._build_use_case(need_to_sync=False, need_to_backup=True)
        use_case.fetch_thies_file_names = AsyncMock(return_value={("AVG_a.BIN", 10)})
        use_case._fill_local_backup = AsyncMock(return_value={"AVG_a.BIN"})
        use_case._extract_thies_daily_statistics = AsyncMock(return_value=None)

        result = await use_case.execute()

        self.assertTrue(result["need_to_backup"])
        self.assertFalse(result["need_to_sync"])
        self.assertIn("backup", result)
        self.assertNotIn("sync", result)

    async def test_should_execute_sync_only(self):
        use_case = self._build_use_case(need_to_sync=True, need_to_backup=False)
        use_case.fetch_local_backup_file_names = AsyncMock(
            return_value={("AVG_sensor_a.BIN", 10)}
        )
        use_case.fetch_cloud_file_names = AsyncMock(
            return_value={("AVG_sensor_a.BIN", 10)}
        )
        use_case._sync_pending_files = AsyncMock(return_value={"AVG_sensor_a.BIN"})
        use_case.fetch_local_backup_file_content = AsyncMock(
            return_value={"AVG_sensor_a.BIN": b"content-a"}
        )
        use_case.upload_thies_files_to_cloud = AsyncMock(
            return_value={"failed_files": [], "new_files": ["AVG_sensor_a.BIN"]}
        )

        result = await use_case.execute()

        self.assertFalse(result["need_to_backup"])
        self.assertTrue(result["need_to_sync"])
        self.assertIn("sync", result)

    async def test_should_execute_sync_only_without_uploading_anything(self):
        use_case = self._build_use_case(need_to_sync=True, need_to_backup=False)
        use_case.fetch_local_backup_file_names = AsyncMock(
            return_value={("AVG_sensor_a.BIN", 10)}
        )
        use_case.fetch_cloud_file_names = AsyncMock(
            return_value={("AVG_sensor_a.BIN", 10)}
        )
        use_case._sync_pending_files = AsyncMock(return_value=set())

        result = await use_case.execute()

        self.assertEqual(
            result["sync"],
            {"failed_files": [], "new_files": [], "processed_files": {}},
        )
