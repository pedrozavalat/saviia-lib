import os
from logging import Logger
from typing import Any, Dict, Set

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    CloudClientFetchingError,
    ThiesConnectionError,
    ThiesFetchingError,
)
from saviialib.general_types.error_types.common import CloudClientError, FtpClientError
from saviialib.libs.cloud_client import CloudClientListFilesArgs
from saviialib.libs.ftp_client import FtpListFilesArgs
from saviialib.libs.log_client import LogStatus

from .base import ThiesComponent
from .directories import ThiesDirectoryComponent
from .paths import THIES_CATEGORIES, ThiesPathComponent


class ThiesInventoryComponent(ThiesComponent):
    """Read and normalize FTP, local, and cloud THIES inventories."""

    def __init__(
        self,
        paths: ThiesPathComponent,
        ftp_client: Any,
        directory_client: Any,
        cloud_client: Any,
        directories: ThiesDirectoryComponent,
        logger: Logger | None = None,
    ) -> None:
        super().__init__("thies_inventory", logger)
        self.paths = paths
        self.ftp_client = ftp_client
        self.directory_client = directory_client
        self.cloud_client = cloud_client
        self.directories = directories

    @staticmethod
    def extract_local_entry(entry: Any) -> tuple[str, int | None]:
        if isinstance(entry, tuple):
            name = entry[0]
            size = entry[1] if len(entry) > 1 else None
            return name, int(size) if size is not None else None
        return str(entry), None

    async def list_local_files_with_sizes(
        self, folder_path: str
    ) -> list[tuple[str, int]]:
        entries = await self.directory_client.listdir(folder_path)
        file_sizes: list[tuple[str, int]] = []
        for entry in entries:
            filename, entry_size = self.extract_local_entry(entry)
            file_path = self.directory_client.join_paths(folder_path, filename)
            if await self.directory_client.isdir(file_path):
                continue
            if entry_size is not None:
                size = entry_size
            elif os.path.exists(file_path):
                size = os.path.getsize(file_path)
            else:
                size = 0
            file_sizes.append((filename, int(size)))
        return file_sizes

    async def get_local_summary(
        self, ensure_structure: bool = True, require_root: bool = True
    ) -> Dict[str, int | Set[str] | Dict[str, int]]:
        method_name = "get_local_summary"
        if ensure_structure:
            await self.directories.ensure_local_structure(require_root=require_root)

        self._debug(
            method_name,
            LogStatus.STARTED,
            f"Listing local files under '{self.paths.get_local_thies_path()}'",
        )
        entries_by_category = {
            category: await self.list_local_files_with_sizes(
                self.paths.get_local_folder(category)
            )
            for category in THIES_CATEGORIES
        }
        filenames = {
            f"{category}_{name}"
            for category, entries in entries_by_category.items()
            for name, _ in entries
        }
        file_sizes = {
            f"{category}_{name}": size
            for category, entries in entries_by_category.items()
            for name, size in entries
        }
        result: Dict[str, int | Set[str] | Dict[str, int]] = {
            "filenames": filenames,
            "file_sizes": file_sizes,
            "count_avg_files": len(entries_by_category["AVG"]),
            "count_ext_files": len(entries_by_category["EXT"]),
        }
        self._debug(
            method_name,
            LogStatus.SUCCESSFUL,
            (
                f"Local inventory: total={len(filenames)}, "
                f"AVG={len(entries_by_category['AVG'])}, "
                f"EXT={len(entries_by_category['EXT'])}"
            ),
        )
        return result

    async def get_local_files(self) -> Set[tuple[str, int]]:
        summary = await self.get_local_summary(
            ensure_structure=False,
            require_root=False,
        )
        filenames = summary["filenames"]
        file_sizes = summary["file_sizes"]
        assert isinstance(filenames, set)
        assert isinstance(file_sizes, dict)
        return {(name, int(file_sizes[name])) for name in filenames}

    async def get_ftp_files(
        self, ftp_folders: list[str] | None = None
    ) -> Set[tuple[str, int]]:
        method_name = "get_ftp_files"
        if self.ftp_client is None:
            raise FtpClientError("FTP client was not initialized.")

        folders = ftp_folders or self.paths.ftp_folders
        self._debug(
            method_name,
            LogStatus.STARTED,
            f"Listing FTP files from {len(folders)} folders",
        )
        folder_path = ""
        try:
            files_inventory: Set[tuple[str, int]] = set()
            for folder_path in folders:
                category = self.paths.category_from_ftp_path(folder_path)
                files = await self.ftp_client.list_files(
                    FtpListFilesArgs(path=folder_path)
                )
                category_files = {
                    (f"{category}_{name}", int(size)) for name, size in files
                }
                files_inventory.update(category_files)
                self._debug(
                    method_name,
                    LogStatus.SUCCESSFUL,
                    (
                        f"Listed {len(category_files)} {category} files "
                        f"from '{folder_path}'"
                    ),
                )
            return files_inventory
        except ConnectionRefusedError as error:
            self._error(
                method_name,
                f"FTP connection refused while listing '{folder_path}'",
                error,
            )
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            self._error(
                method_name,
                f"FTP connection aborted while listing '{folder_path}'",
                error,
            )
            raise ThiesFetchingError(reason=error)

    @staticmethod
    def normalize_cloud_response(response: Any) -> list[tuple[str, int]]:
        if isinstance(response, dict):
            return [
                (item["Name"], int(item["Length"]))
                for item in response.get("value", [])
            ]
        return [
            (item["name"], int(item.get("file_size", 0)))
            for item in response
            if not item.get("is_directory", False)
        ]

    async def get_cloud_files(
        self,
        ensure_structure: bool = False,
        wrap_errors: bool = True,
    ) -> Set[tuple[str, int]]:
        method_name = "get_cloud_files"
        if self.cloud_client is None:
            raise CloudClientError("SAVIIA Cloud client provider was not initialized.")
        if not self.paths.cloud_destination_path:
            raise ValueError("Cloud provider destination path is not configured")

        cloud_thies_path = self.paths.get_cloud_thies_path()
        relative_url = cloud_thies_path
        self._debug(
            method_name,
            LogStatus.STARTED,
            f"Listing cloud files under '{cloud_thies_path}'",
        )
        try:
            if ensure_structure:
                await self.directories.ensure_cloud_structure()
            cloud_files: Set[tuple[str, int]] = set()
            async with self.cloud_client:
                for category in THIES_CATEGORIES:
                    relative_url = self.paths.get_cloud_folder(category)
                    response = await self.cloud_client.list_files(
                        CloudClientListFilesArgs(folder_relative_url=relative_url)
                    )
                    entries = self.normalize_cloud_response(response)
                    cloud_files.update(
                        (f"{category}_{name}", size) for name, size in entries
                    )
                    self._debug(
                        method_name,
                        LogStatus.SUCCESSFUL,
                        f"Listed {len(entries)} files from '{relative_url}'",
                    )
            return cloud_files
        except Exception as error:
            self._error(
                method_name,
                f"Could not list cloud files from '{relative_url}'",
                error,
            )
            if wrap_errors:
                raise CloudClientFetchingError(reason=error)
            raise
