from logging import Logger
from typing import Any, Set, cast

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ThiesConnectionError,
    ThiesFetchingError,
)
from saviialib.general_types.error_types.common import FtpClientError
from saviialib.libs.files_client import WriteArgs
from saviialib.libs.ftp_client import FtpReadFileArgs
from saviialib.libs.log_client import LogStatus
from saviialib.libs.zero_dependency.utils.datetime_utils import datetime_to_str, today

from .base import ThiesComponent
from .inventory import ThiesInventoryComponent
from .paths import THIES_CATEGORIES, ThiesCategory, ThiesPathComponent
from .create_thies_statistics_file import create_thies_daily_statistics_file


class ThiesBackupComponent(ThiesComponent):
    """Copy pending THIES files from FTP into the local backup."""

    def __init__(
        self,
        paths: ThiesPathComponent,
        inventory: ThiesInventoryComponent,
        ftp_client: Any,
        files_client: Any,
        directory_client: Any,
        logger: Logger | None = None,
    ) -> None:
        super().__init__("thies_backup", logger)
        self.paths = paths
        self.inventory = inventory
        self.ftp_client = ftp_client
        self.files_client = files_client
        self.directory_client = directory_client
        self.logger = logger

    async def backup_files(self, thies_files: Set[tuple[str, int]]) -> Set[str]:
        method_name = "backup_files"
        self._debug(
            method_name,
            LogStatus.STARTED,
            f"Evaluating {len(thies_files)} FTP files for local backup",
        )
        local_files = await self.inventory.get_local_files()
        local_sizes = {name: int(size) for name, size in local_files}
        saved_files: Set[str] = set()
        try:
            for file_key, ftp_size in thies_files:
                category_value, filename = file_key.split("_", 1)
                category = cast(ThiesCategory, category_value)
                local_size = local_sizes.get(file_key)
                # Preserve the original behavior: a zero-byte local file is treated
                # as incomplete and downloaded again.
                if local_size is not None and local_size > 0 and local_size == ftp_size:
                    continue
                if self.ftp_client is None:
                    raise FtpClientError("FTP client was not initialized.")

                ftp_folder = self.paths.get_ftp_folder(category)
                destination = self.paths.get_local_folder(category)
                source_path = f"{ftp_folder.rstrip('/')}/{filename}"
                self._debug(
                    method_name,
                    LogStatus.STARTED,
                    f"Downloading '{file_key}' from '{source_path}'",
                )
                content = await self.ftp_client.read_file(FtpReadFileArgs(source_path))
                await self.files_client.write(
                    WriteArgs(
                        file_name=filename,
                        file_content=content,
                        mode="wb",
                        destination_path=destination,
                    )
                )
                saved_files.add(file_key)
                self._debug(
                    method_name,
                    LogStatus.SUCCESSFUL,
                    f"Saved '{file_key}' to '{destination}'",
                )
        except ConnectionRefusedError as error:
            self._error(method_name, "FTP connection refused during backup", error)
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            self._error(method_name, "FTP connection aborted during backup", error)
            raise ThiesFetchingError(reason=error)

        self._debug(
            method_name,
            LogStatus.SUCCESSFUL,
            f"Local backup completed: saved={len(saved_files)}",
        )
        return saved_files

    async def generate_daily_statistics(self) -> None:
        method_name = "generate_daily_statistics"
        date_filename = datetime_to_str(today(), date_format="%Y%m%d") + ".BIN"
        self._debug(
            method_name,
            LogStatus.STARTED,
            f"Checking daily file '{date_filename}' for AVG and EXT",
        )
        for category in THIES_CATEGORIES:
            folder_path = self.paths.get_local_folder(category)
            files = await self.directory_client.listdir(folder_path)
            if date_filename not in files:
                self._warning(
                    method_name,
                    (
                        f"Skipping statistics: '{date_filename}' not found "
                        f"in '{folder_path}'"
                    ),
                )
                return
        await create_thies_daily_statistics_file(
            self.paths.local_backup_path,
            self.directory_client,
            self.logger,
        )
        self._debug(
            method_name,
            LogStatus.SUCCESSFUL,
            "Daily THIES statistics generated successfully",
        )
