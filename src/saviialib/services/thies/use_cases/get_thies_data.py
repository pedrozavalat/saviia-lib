from typing import Dict, Mapping, Set

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
    ThiesConnectionError,
    ThiesFetchingError,
)
from saviialib.general_types.error_types.common import FtpClientError
from saviialib.libs.log_client import (
    DebugArgs,
    ErrorArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
)
from saviialib.services.thies.use_cases.components import (
    ThiesDirectoryComponent,
    ThiesInventoryComponent,
    ThiesPathComponent,
    ThiesSyncPlanner,
)
from saviialib.services.thies.use_cases.types.get_thies_data_types import (
    GetThiesDataUseCaseInput,
    GetThiesDataUseCaseOutput,
)


class GetThiesDataUseCase:
    """Inspect THIES inventories and report required backup and sync work."""

    DEFAULT_FTP_FOLDERS = ["/ARCH_AV1", "/ARCH_EX1"]

    def __init__(self, input: GetThiesDataUseCaseInput):
        self.cloud_client = input.cloud_client
        self.thies_ftp_client = input.ftp_client
        self.files_client = input.files_client
        self.dir_client = input.directory_client
        self.local_backup_path = input.local_backup_path
        self.cloud_provider_destination_path = input.cloud_provider_destination_path
        self.sync_error = False
        self.uploading: set[str] = set()
        self.logger = LogClient(
            LogClientArgs(
                client_name="logging",
                service_name="thies",
                class_name="get_thies_data",
                logger=input.logger,
            )
        )

        self.paths = ThiesPathComponent(
            local_backup_path=self.local_backup_path,
            cloud_destination_path=self.cloud_provider_destination_path,
            ftp_folders=self.DEFAULT_FTP_FOLDERS,
        )
        self.cloud_base_path = self.paths.get_cloud_thies_path()
        self.directories = ThiesDirectoryComponent(
            self.paths,
            self.dir_client,
            self.cloud_client,
            input.logger,
        )
        self.inventory = ThiesInventoryComponent(
            self.paths,
            self.thies_ftp_client,
            self.dir_client,
            self.cloud_client,
            self.directories,
            input.logger,
        )
        self.planner = ThiesSyncPlanner(input.logger)

    async def _list_local_files_with_sizes(
        self, folder_path: str
    ) -> list[tuple[str, int]]:
        return await self.inventory.list_local_files_with_sizes(folder_path)

    async def _fetch_local_backup_files(
        self,
    ) -> Dict[str, int | Set[str] | Dict[str, int]]:
        return await self.inventory.get_local_summary(
            ensure_structure=True,
            require_root=True,
        )

    async def _fetch_cloud_total_files(self) -> Set[tuple[str, int]]:
        if not self.cloud_provider_destination_path:
            raise BackupSourcePathError(
                reason="Cloud provider destination path is not configured"
            )
        return await self.inventory.get_cloud_files(
            ensure_structure=False,
            wrap_errors=False,
        )

    async def _fetch_thies_total_files(self) -> Set[tuple[str, int]]:
        try:
            return await self.inventory.get_ftp_files(self.DEFAULT_FTP_FOLDERS)
        except ThiesConnectionError as error:
            raise ThiesFetchingError(reason=error) from error

    def _validate_pending_files(
        self,
        thies_files: Set[tuple[str, int]],
        cloud_files: Set[tuple[str, int]],
        backup_files: Mapping[str, object],
    ) -> dict[str, int | bool]:
        plan = self.planner.create_plan(
            thies_files,
            cloud_files,
            backup_files,
            sync_error=self.sync_error,
        )
        return {
            "need_to_backup": plan.need_to_backup,
            "need_to_sync": plan.need_to_sync,
            "total_to_backup": len(plan.files_to_backup),
            "total_to_sync": len(plan.files_to_sync),
        }

    async def execute(self) -> GetThiesDataUseCaseOutput:
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(status=LogStatus.STARTED))
        try:
            backup_files = await self._fetch_local_backup_files()
        except OSError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": str(error)})
            )
            raise BackupSourcePathError(reason=error)

        try:
            thies_files = await self._fetch_thies_total_files()
        except RuntimeError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": str(error)})
            )
            raise FtpClientError(error)

        try:
            cloud_files = await self._fetch_cloud_total_files()
        except (RuntimeError, ConnectionError) as error:
            self.sync_error = True
            cloud_files = set()
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": str(error)})
            )

        validation = self._validate_pending_files(
            thies_files,
            cloud_files,
            backup_files,
        )
        return GetThiesDataUseCaseOutput(
            need_to_sync=bool(validation["need_to_sync"]),
            need_to_backup=bool(validation["need_to_backup"]),
            total_to_backup=int(validation["total_to_backup"]),
            total_to_sync=int(validation["total_to_sync"]),
        )
