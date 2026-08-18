from typing import Any, Dict, List, Set, Tuple

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
)
from saviialib.general_types.error_types.common import EmptyDataError, FtpClientError
from saviialib.libs.log_client import (
    DebugArgs,
    ErrorArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
    WarningArgs,
)
from saviialib.services.thies.use_cases.components import (
    ThiesBackupComponent,
    ThiesCloudSyncComponent,
    ThiesDirectoryComponent,
    ThiesInventoryComponent,
    ThiesPathComponent,
    ThiesSyncPlanner,
)
from saviialib.services.thies.use_cases.types.post_thies_data_types import (
    PostThiesDataUseCaseInput,
)
from saviialib.services.thies.use_cases.utils.post_thies_data_utils import (
    parse_execute_response,
)


class PostThiesDataUseCase:
    """Orchestrate THIES backup and cloud synchronization components."""

    BASE_FOLDER_NAME = "thies"

    def __init__(self, input: PostThiesDataUseCaseInput):
        self.need_to_sync = input.need_to_sync
        self.need_to_backup = input.need_to_backup
        self.cloud_client = input.cloud_client
        self.logger = input.logger
        self.thies_ftp_client = input.ftp_client
        self.cloud_provider_destination_path = input.cloud_provider_destination_path
        self.ftp_server_folders_path = input.ftp_server_folders_path
        self.local_backup_path = input.local_backup_source_path
        self.uploading: Set[str] = set()
        self.os_client = input.directory_client
        self.files_client = input.files_client
        self.log_client = LogClient(
            LogClientArgs(
                client_name="logging",
                service_name="thies",
                class_name="post_thies_data",
                logger=input.logger,
            )
        )

        self.paths = ThiesPathComponent(
            local_backup_path=self.local_backup_path,
            cloud_destination_path=self.cloud_provider_destination_path,
            ftp_folders=self.ftp_server_folders_path,
        )
        self.directories = ThiesDirectoryComponent(
            self.paths,
            self.os_client,
            self.cloud_client,
            input.logger,
        )
        self.inventory = ThiesInventoryComponent(
            self.paths,
            self.thies_ftp_client,
            self.os_client,
            self.cloud_client,
            self.directories,
            input.logger,
        )
        self.planner = ThiesSyncPlanner(input.logger)
        self.backup = ThiesBackupComponent(
            self.paths,
            self.inventory,
            self.thies_ftp_client,
            self.files_client,
            self.os_client,
            input.logger,
        )
        self.cloud_sync = ThiesCloudSyncComponent(
            self.paths,
            self.files_client,
            self.cloud_client,
            input.logger,
        )

    def _debug(self, status: LogStatus, message: str = "") -> None:
        self.log_client.method_name = "execute"
        metadata = {"msg": message} if message else {}
        self.log_client.debug(DebugArgs(status=status, metadata=metadata))

    def _error(self, message: str, error: Exception) -> None:
        self.log_client.method_name = "execute"
        self.log_client.error(
            ErrorArgs(
                status=LogStatus.ERROR,
                metadata={"msg": f"{message}; error={type(error).__name__}: {error}"},
            )
        )

    # Compatibility facades. Existing callers can keep using the original methods.
    def _cloud_provider_thies_base_path(self) -> str:
        return self.paths.get_cloud_thies_path()

    @staticmethod
    def _extract_local_entry(entry: Any) -> tuple[str, int | None]:
        return ThiesInventoryComponent.extract_local_entry(entry)

    async def _validate_cloud_destination(self) -> None:
        await self.directories.ensure_cloud_structure()

    async def _validate_sharepoint_destination(self) -> None:
        """Backward-compatible alias for the provider-neutral validation method."""
        await self._validate_cloud_destination()

    async def fetch_cloud_file_names(self) -> Set[Tuple[str, int]]:
        return await self.inventory.get_cloud_files(ensure_structure=True)

    async def fetch_thies_file_names(self) -> Set[Tuple[str, int]]:
        return await self.inventory.get_ftp_files()

    async def fetch_local_backup_file_names(self) -> Set[Tuple[str, int]]:
        return await self.inventory.get_local_files()

    async def fetch_local_backup_file_content(self) -> Dict[str, bytes]:
        return await self.cloud_sync.read_local_files(self.uploading)

    async def upload_thies_files_to_cloud(
        self, files: Dict[str, bytes]
    ) -> Dict[str, List[str]]:
        return await self.cloud_sync.upload_files(files)

    async def upload_thies_files_to_sharepoint(
        self, files: Dict[str, bytes]
    ) -> Dict[str, List[str]]:
        """Backward-compatible alias for the provider-neutral upload method."""
        return await self.upload_thies_files_to_cloud(files)

    async def _sync_pending_files(
        self,
        local_files: Set[Tuple[str, int]],
        cloud_files: Set[Tuple[str, int]],
    ) -> Set[str]:
        return self.planner.get_files_to_sync(local_files, cloud_files)

    async def _extract_thies_daily_statistics(self) -> None:
        await self.backup.generate_daily_statistics()

    async def _validate_local_backup(self) -> None:
        await self.directories.ensure_local_structure()

    async def _fill_local_backup(
        self, thies_files: Set[Tuple[str, int]]
    ) -> Set[str]:
        return await self.backup.backup_files(thies_files)

    async def execute(self) -> Dict[str, Any]:
        self._debug(
            LogStatus.STARTED,
            (
                f"Starting post THIES workflow: backup={self.need_to_backup}, "
                f"sync={self.need_to_sync}, local='{self.local_backup_path}', "
                f"cloud='{self.cloud_provider_destination_path}'"
            ),
        )
        if not self.need_to_backup and not self.need_to_sync:
            self.log_client.warning(
                WarningArgs(
                    status=LogStatus.FAILED,
                    metadata={"msg": "No backup or sync operation was requested"},
                )
            )
            raise EmptyDataError(reason="No backup or sync requested.")

        try:
            await self._validate_local_backup()
        except OSError as error:
            self._error(
                f"Could not prepare local backup '{self.local_backup_path}'",
                error,
            )
            raise BackupSourcePathError(reason=error)

        result: Dict[str, Any] = {
            "need_to_backup": self.need_to_backup,
            "need_to_sync": self.need_to_sync,
        }

        if self.need_to_backup:
            self._debug(LogStatus.STARTED, "Starting FTP backup stage")
            try:
                thies_files = await self.fetch_thies_file_names()
                backed_up_files = await self._fill_local_backup(thies_files)
            except RuntimeError as error:
                self._error("FTP backup stage failed", error)
                raise FtpClientError(error)
            await self._extract_thies_daily_statistics()
            result["backup"] = {
                "backed_up_files": sorted(backed_up_files),
                "total": len(backed_up_files),
            }
            self._debug(
                LogStatus.SUCCESSFUL,
                f"FTP backup stage completed: saved={len(backed_up_files)}",
            )

        if self.need_to_sync:
            self._debug(LogStatus.STARTED, "Starting cloud sync stage")
            try:
                local_files = await self.fetch_local_backup_file_names()
            except OSError as error:
                self._error(
                    f"Could not read local backup '{self.local_backup_path}'",
                    error,
                )
                raise BackupSourcePathError(reason=error)

            cloud_files = await self.fetch_cloud_file_names()
            self.uploading = await self._sync_pending_files(local_files, cloud_files)
            if self.uploading:
                local_backup_files = await self.fetch_local_backup_file_content()
                upload_statistics = await self.upload_thies_files_to_cloud(
                    local_backup_files
                )
                result["sync"] = parse_execute_response(
                    local_backup_files,
                    upload_statistics,
                )
            else:
                result["sync"] = {
                    "failed_files": [],
                    "new_files": [],
                    "processed_files": {},
                }

            sync_result = result["sync"]
            self._debug(
                LogStatus.SUCCESSFUL,
                (
                    "Cloud sync stage completed: "
                    f"pending={len(self.uploading)}, "
                    f"uploaded={len(sync_result.get('new_files', []))}, "
                    f"failed={len(sync_result.get('failed_files', []))}"
                ),
            )

        self._debug(
            LogStatus.SUCCESSFUL,
            (
                f"Completed post THIES workflow: backup={self.need_to_backup}, "
                f"sync={self.need_to_sync}"
            ),
        )
        return result
