from logging import Logger
from typing import Any

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
)
from saviialib.general_types.error_types.common import CloudClientError
from saviialib.libs.cloud_client import CloudClientCreateFolderArgs
from saviialib.libs.log_client import LogStatus

from .base import ThiesComponent
from .paths import THIES_CATEGORIES, ThiesPathComponent


class ThiesDirectoryComponent(ThiesComponent):
    """Validate and provision local and cloud THIES directory structures."""

    def __init__(
        self,
        paths: ThiesPathComponent,
        directory_client: Any,
        cloud_client: Any,
        logger: Logger | None = None,
    ) -> None:
        super().__init__("thies_directories", logger)
        self.paths = paths
        self.directory_client = directory_client
        self.cloud_client = cloud_client

    async def ensure_local_structure(self, require_root: bool = False) -> None:
        method_name = "ensure_local_structure"
        local_root = self.paths.local_backup_path
        if require_root and not await self.directory_client.path_exists(local_root):
            raise BackupSourcePathError(
                reason=f"Local Backup path '{local_root}' doesn't exist"
            )

        local_thies_path = self.paths.get_local_thies_path()
        self._debug(
            method_name,
            LogStatus.STARTED,
            f"Ensuring local directories under '{local_thies_path}'",
        )
        for folder_path in (
            local_thies_path,
            *(self.paths.get_local_folder(category) for category in THIES_CATEGORIES),
        ):
            if not await self.directory_client.path_exists(folder_path):
                await self.directory_client.makedirs(folder_path)
                self._debug(
                    method_name,
                    LogStatus.SUCCESSFUL,
                    f"Created local directory '{folder_path}'",
                )
        self._debug(
            method_name,
            LogStatus.SUCCESSFUL,
            f"Local destination ready: '{local_thies_path}'",
        )

    async def ensure_cloud_structure(self) -> None:
        method_name = "ensure_cloud_structure"
        if self.cloud_client is None:
            raise CloudClientError("Cloud Client was not initialized.")

        cloud_thies_path = self.paths.get_cloud_thies_path()
        self._debug(
            method_name,
            LogStatus.STARTED,
            f"Ensuring cloud directories under '{cloud_thies_path}'",
        )
        try:
            async with self.cloud_client:
                for folder_path in (
                    cloud_thies_path,
                    *(
                        self.paths.get_cloud_folder(category)
                        for category in THIES_CATEGORIES
                    ),
                ):
                    await self.cloud_client.create_folder(
                        CloudClientCreateFolderArgs(folder_relative_url=folder_path)
                    )
                    self._debug(
                        method_name,
                        LogStatus.SUCCESSFUL,
                        f"Cloud directory ready: '{folder_path}'",
                    )
        except Exception as error:
            self._error(
                method_name,
                f"Could not prepare cloud destination '{cloud_thies_path}'",
                error,
            )
            raise
