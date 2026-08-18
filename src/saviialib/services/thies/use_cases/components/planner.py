from dataclasses import dataclass
from logging import Logger
from typing import Dict, Mapping, Set, cast

from saviialib.libs.log_client import LogStatus

from .base import ThiesComponent


@dataclass(frozen=True)
class ThiesSyncPlan:
    files_to_backup: set[str]
    files_to_sync: set[str]
    backup_required: bool = False

    @property
    def need_to_backup(self) -> bool:
        return self.backup_required or bool(self.files_to_backup)

    @property
    def need_to_sync(self) -> bool:
        return bool(self.files_to_sync)


class ThiesSyncPlanner(ThiesComponent):
    """Compare THIES inventories without performing any I/O."""

    def __init__(self, logger: Logger | None = None) -> None:
        super().__init__("thies_sync_planner", logger)

    @staticmethod
    def sizes_match(source_size: int, destination_size: int) -> bool:
        return (
            source_size == 0
            or destination_size == 0
            or source_size == destination_size
        )

    def get_files_to_sync(
        self,
        local_files: Set[tuple[str, int]],
        cloud_files: Set[tuple[str, int]],
    ) -> set[str]:
        method_name = "get_files_to_sync"
        self._debug(
            method_name,
            LogStatus.STARTED,
            f"Comparing local={len(local_files)} and cloud={len(cloud_files)} files",
        )
        local_files_dict = {name: int(size) for name, size in local_files}
        cloud_files_dict = {name: int(size) for name, size in cloud_files}
        pending = {
            name
            for name, local_size in local_files_dict.items()
            if name not in cloud_files_dict
            or not self.sizes_match(local_size, cloud_files_dict[name])
        }
        self._debug(
            method_name,
            LogStatus.SUCCESSFUL,
            f"Pending files to sync: {len(pending)}",
        )
        return pending

    def create_plan(
        self,
        thies_files: Set[tuple[str, int]],
        cloud_files: Set[tuple[str, int]],
        backup_files: Mapping[str, object],
        sync_error: bool = False,
    ) -> ThiesSyncPlan:
        method_name = "create_plan"
        self._debug(method_name, LogStatus.STARTED, "Comparing THIES inventories")
        thies_files_dict = {name: int(size) for name, size in thies_files}
        cloud_files_dict = {name: int(size) for name, size in cloud_files}
        backup_filenames = cast(Set[str], backup_files["filenames"])
        backup_file_sizes = cast(Dict[str, int], backup_files.get("file_sizes", {}))
        count_ext_files = cast(int, backup_files.get("count_ext_files", 0))
        count_avg_files = cast(int, backup_files.get("count_avg_files", 0))

        files_to_backup = set(thies_files_dict).difference(backup_filenames)
        for file_name, thies_size in thies_files_dict.items():
            if (
                file_name in backup_file_sizes
                and backup_file_sizes[file_name] != thies_size
            ):
                files_to_backup.add(file_name)

        files_to_sync = set()
        if not sync_error:
            files_to_sync = {
                name
                for name, thies_size in thies_files_dict.items()
                if name not in cloud_files_dict
                or not self.sizes_match(thies_size, cloud_files_dict[name])
            }

        plan = ThiesSyncPlan(
            files_to_backup,
            files_to_sync,
            backup_required=count_ext_files != count_avg_files,
        )
        self._debug(
            method_name,
            LogStatus.SUCCESSFUL,
            (
                f"Plan created: backup={plan.need_to_backup} "
                f"({len(plan.files_to_backup)}), sync={plan.need_to_sync} "
                f"({len(plan.files_to_sync)})"
            ),
        )
        return plan
