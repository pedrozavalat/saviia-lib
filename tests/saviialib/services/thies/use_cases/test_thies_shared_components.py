import logging
import os
import unittest
from unittest.mock import AsyncMock, MagicMock

from saviialib.services.thies.use_cases.components import (
    ThiesDirectoryComponent,
    ThiesInventoryComponent,
    ThiesPathComponent,
    ThiesSyncPlanner,
)
from saviialib.services.thies.use_cases.get_thies_data import GetThiesDataUseCase
from saviialib.services.thies.use_cases.post_thies_data import PostThiesDataUseCase
from saviialib.services.thies.use_cases.types.get_thies_data_types import (
    GetThiesDataUseCaseInput,
)
from saviialib.services.thies.use_cases.types.post_thies_data_types import (
    PostThiesDataUseCaseInput,
)


CLOUD_ROOT = "/Volumes/arquitectura_dev/saviia_test/archivos_telemetry"
LOCAL_ROOT = "saviia-local-backup"


def build_clients():
    directory = MagicMock()
    directory.join_paths.side_effect = os.path.join
    directory.path_exists = AsyncMock(return_value=True)
    directory.makedirs = AsyncMock()
    directory.listdir = AsyncMock(return_value=[])
    directory.isdir = AsyncMock(return_value=False)
    directory.get_basename.side_effect = os.path.basename

    cloud = MagicMock()
    cloud.__aenter__ = AsyncMock(return_value=cloud)
    cloud.__aexit__ = AsyncMock(return_value=None)
    cloud.create_folder = AsyncMock(return_value={})
    cloud.list_files = AsyncMock(return_value=[])
    cloud.upload_file = AsyncMock(return_value={})

    ftp = MagicMock()
    ftp.list_files = AsyncMock(return_value=[])
    ftp.read_file = AsyncMock(return_value=b"")

    files = MagicMock()
    files.read = AsyncMock(return_value=b"")
    files.write = AsyncMock(return_value=None)
    return directory, cloud, ftp, files


class TestThiesPathComponent(unittest.TestCase):
    def test_builds_consistent_local_and_cloud_paths(self):
        paths = ThiesPathComponent(
            LOCAL_ROOT,
            CLOUD_ROOT,
            ["/ARCH_AV1", "/ARCH_EX1"],
        )

        self.assertEqual(paths.get_local_folder("EXT"), f"{LOCAL_ROOT}/thies/EXT")
        self.assertEqual(
            paths.get_cloud_folder("EXT"),
            f"{CLOUD_ROOT}/{LOCAL_ROOT}/thies/EXT",
        )
        self.assertEqual(paths.get_ftp_folder("AVG"), "/ARCH_AV1")
        self.assertEqual(paths.get_ftp_folder("EXT"), "/ARCH_EX1")

    def test_uses_only_local_backup_name_inside_cloud_path(self):
        paths = ThiesPathComponent(
            "/tmp/backups/saviia-local-backup",
            CLOUD_ROOT,
        )

        self.assertEqual(
            paths.get_cloud_folder("EXT"),
            f"{CLOUD_ROOT}/saviia-local-backup/thies/EXT",
        )


class TestThiesSyncPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = ThiesSyncPlanner(logging.getLogger("test"))

    def test_keeps_zero_size_as_unknown_when_planning_cloud_sync(self):
        pending = self.planner.get_files_to_sync(
            {("AVG_a.bin", 10), ("EXT_b.bin", 0), ("EXT_c.bin", 30)},
            {("AVG_a.bin", 10), ("EXT_b.bin", 20)},
        )

        self.assertEqual(pending, {"EXT_c.bin"})

    def test_preserves_inventory_imbalance_rule_without_inventing_a_file(self):
        plan = self.planner.create_plan(
            {("AVG_a.bin", 10)},
            {("AVG_a.bin", 10)},
            {
                "filenames": {"AVG_a.bin"},
                "file_sizes": {"AVG_a.bin": 10},
                "count_avg_files": 1,
                "count_ext_files": 0,
            },
        )

        self.assertTrue(plan.need_to_backup)
        self.assertEqual(plan.files_to_backup, set())


class TestThiesInventoryComponent(unittest.IsolatedAsyncioTestCase):
    async def test_lists_databricks_folders_with_shared_path_component(self):
        directory, cloud, ftp, _ = build_clients()
        paths = ThiesPathComponent(LOCAL_ROOT, CLOUD_ROOT)
        directories = ThiesDirectoryComponent(paths, directory, cloud)
        inventory = ThiesInventoryComponent(
            paths,
            ftp,
            directory,
            cloud,
            directories,
        )

        async def list_files(args):
            filename = (
                "avg.bin"
                if args.folder_relative_url.endswith("/AVG")
                else "ext.bin"
            )
            return [{"name": filename, "file_size": 10, "is_directory": False}]

        cloud.list_files = AsyncMock(side_effect=list_files)
        result = await inventory.get_cloud_files()

        self.assertEqual(result, {("AVG_avg.bin", 10), ("EXT_ext.bin", 10)})
        requested_paths = [
            call.args[0].folder_relative_url
            for call in cloud.list_files.await_args_list
        ]
        self.assertEqual(
            requested_paths,
            [
                f"{CLOUD_ROOT}/{LOCAL_ROOT}/thies/AVG",
                f"{CLOUD_ROOT}/{LOCAL_ROOT}/thies/EXT",
            ],
        )


class TestUseCaseComposition(unittest.TestCase):
    def test_get_and_post_share_the_same_cloud_path_rule(self):
        directory, cloud, ftp, files = build_clients()
        get_use_case = GetThiesDataUseCase(
            GetThiesDataUseCaseInput(
                ftp_client=ftp,
                cloud_client=cloud,
                files_client=files,
                directory_client=directory,
                local_backup_path=LOCAL_ROOT,
                cloud_provider_destination_path=CLOUD_ROOT,
                logger=logging.getLogger("test"),
            )
        )
        post_use_case = PostThiesDataUseCase(
            PostThiesDataUseCaseInput(
                ftp_client=ftp,
                cloud_client=cloud,
                files_client=files,
                directory_client=directory,
                cloud_provider_destination_path=CLOUD_ROOT,
                ftp_server_folders_path=["/ARCH_AV1", "/ARCH_EX1"],
                local_backup_source_path=LOCAL_ROOT,
                need_to_sync=True,
                need_to_backup=False,
                logger=logging.getLogger("test"),
            )
        )

        expected = f"{CLOUD_ROOT}/{LOCAL_ROOT}/thies"
        self.assertEqual(get_use_case.cloud_base_path, expected)
        self.assertEqual(post_use_case._cloud_provider_thies_base_path(), expected)
