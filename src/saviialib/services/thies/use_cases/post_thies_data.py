from typing import Any, Dict, List, Set, Tuple

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
    SharePointFetchingError,
    SharePointUploadError,
    ThiesConnectionError,
    ThiesFetchingError,
)
from saviialib.general_types.error_types.common import (
    EmptyDataError,
    FtpClientError,
    SharepointClientError,
)
from saviialib.libs.files_client import (
    ReadArgs,
    WriteArgs,
)
from saviialib.libs.ftp_client import (
    FtpListFilesArgs,
    FtpReadFileArgs,
)
from saviialib.libs.sharepoint_client import (
    SpListFilesArgs,
    SpCreateFolderArgs,
    SpUploadFileArgs,
)
from saviialib.libs.zero_dependency.utils.datetime_utils import (
    datetime_to_str,
    today,
)
from saviialib.services.thies.use_cases.components.create_thies_statistics_file import (
    create_thies_daily_statistics_file,
)
from saviialib.services.thies.use_cases.types.post_thies_data_types import (
    PostThiesDataUseCaseInput,
)
from saviialib.services.thies.utils.update_thies_data_utils import (
    parse_execute_response,
)


class PostThiesDataUseCase:
    BASE_FOLDER_NAME = "thies"

    def __init__(self, input: PostThiesDataUseCaseInput):
        self.need_to_sync = input.need_to_sync
        self.need_to_backup = input.need_to_backup
        self.sharepoint_client = input.sharepoint_client
        self.logger = input.logger
        self.thies_ftp_client = input.ftp_client
        self.sharepoint_destination_path = input.sharepoint_destination_path
        self.ftp_server_folders_path = input.ftp_server_folders_path
        self.local_backup_path = input.local_backup_source_path
        self.sharepoint_base_url = f"/sites/{self.sharepoint_client.site_name}"
        self.uploading = set()
        self.os_client = input.directory_client
        self.files_client = input.files_client

    def _sharepoint_thies_base_path(self) -> str:
        return f"{self.sharepoint_destination_path}/{PostThiesDataUseCase.BASE_FOLDER_NAME}"

    async def _validate_sharepoint_destination(self):
        if self.sharepoint_client is None:
            raise SharepointClientError("SharePoint client was not initialized.")

        async with self.sharepoint_client:
            sharepoint_thies_path = self._sharepoint_thies_base_path()
            await self.sharepoint_client.create_folder(
                SpCreateFolderArgs(
                    folder_relative_url=sharepoint_thies_path,
                )
            )
            for folder_name in {"AVG", "EXT"}:
                await self.sharepoint_client.create_folder(
                    SpCreateFolderArgs(
                        folder_relative_url=f"{sharepoint_thies_path}/{folder_name}",
                    )
                )

    async def fetch_cloud_file_names(self) -> Set[Tuple[str, int]]:
        if self.sharepoint_client is None:
            raise SharepointClientError("SharePoint client was not initialized.")

        await self._validate_sharepoint_destination()
        try:
            cloud_files: Set[Tuple[str, int]] = set()
            async with self.sharepoint_client:
                sharepoint_thies_path = self._sharepoint_thies_base_path()
                for folder_name in {"AVG", "EXT"}:
                    relative_url = f"{self.sharepoint_base_url}/{sharepoint_thies_path}/{folder_name}"
                    args = SpListFilesArgs(folder_relative_url=relative_url)
                    response = await self.sharepoint_client.list_files(args)
                    cloud_files.update(
                        {
                            (f"{folder_name}_{item['Name']}", int(item["Length"]))
                            for item in response["value"]  # type: ignore
                        }  # type: ignore
                    )
            return cloud_files
        except Exception as error:
            raise SharePointFetchingError(reason=error)

    async def fetch_thies_file_names(self) -> Set[Tuple[str, int]]:
        if self.thies_ftp_client is None:
            raise FtpClientError("FTP client was not initialized.")

        try:
            thies_files: Set[Tuple[str, int]] = set()
            for folder_path in self.ftp_server_folders_path:
                prefix = "AVG" if "AV" in folder_path else "EXT"
                files = await self.thies_ftp_client.list_files(
                    FtpListFilesArgs(path=folder_path)
                )
                files_names = {(f"{prefix}_{name}", int(size)) for name, size in files}
                thies_files.update(files_names)
            return thies_files
        except ConnectionRefusedError as error:
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            raise ThiesFetchingError(reason=error)

    async def fetch_local_backup_file_names(self) -> Set[Tuple[str, int]]:
        thies_avg_files = await self.os_client.listdir(
            self.os_client.join_paths(
                self.local_backup_path, PostThiesDataUseCase.BASE_FOLDER_NAME, "AVG"
            ),
            more_info=True,
        )
        thies_ext_files = await self.os_client.listdir(
            self.os_client.join_paths(
                self.local_backup_path, PostThiesDataUseCase.BASE_FOLDER_NAME, "EXT"
            ),
            more_info=True,
        )
        return {
            *((f"AVG_{filename}", size) for filename, size in thies_avg_files),
            *((f"EXT_{filename}", size) for filename, size in thies_ext_files),
        }

    async def fetch_local_backup_file_content(self) -> Dict[str, bytes]:
        try:
            content_files = {}
            for file in self.uploading:
                prefix, filename = file.split("_", 1)
                file_path = self.os_client.join_paths(
                    self.local_backup_path,
                    PostThiesDataUseCase.BASE_FOLDER_NAME,
                    prefix,
                    filename,
                )
                content = await self.files_client.read(
                    ReadArgs(file_path=file_path, mode="rb")
                )
                self.logger.debug(
                    "[thies_synchronization_lib] Fetching file '%s' from '%s'.",
                    file,
                    file_path,
                )
                content_files[file] = content
            return content_files
        except ConnectionRefusedError as error:
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            raise ThiesFetchingError(reason=error)

    async def upload_thies_files_to_sharepoint(
        self, files: Dict[str, bytes]
    ) -> Dict[str, List[str]]:
        if self.sharepoint_client is None:
            raise SharepointClientError("SharePoint client was not initialized.")

        upload_results = {"failed_files": [], "new_files": []}

        async with self.sharepoint_client:
            sharepoint_thies_path = self._sharepoint_thies_base_path()
            for file, file_content in files.items():
                try:
                    origin, file_name = file.split("_", 1)
                    folder_path = f"{sharepoint_thies_path}/{origin}"
                    relative_url = f"{self.sharepoint_base_url}/{folder_path}"
                    await self.sharepoint_client.upload_file(
                        SpUploadFileArgs(
                            folder_relative_url=relative_url,
                            file_content=file_content,
                            file_name=file_name,
                        )
                    )
                    upload_results["new_files"].append(file)
                    self.logger.debug(
                        "[thies_synchronization_lib] File '%s' uploaded successfully to '%s' ✅",
                        file_name,
                        relative_url,
                    )
                except ConnectionError as error:
                    self.logger.error(
                        "[thies_synchronization_lib] Unexpected error from with file '%s'",
                        file_name,
                    )
                    upload_results["failed_files"].append(
                        f"{file} (Error: {str(error)})"
                    )

        if upload_results["failed_files"]:
            raise SharePointUploadError(
                reason="Files failed to upload: "
                + ", ".join(upload_results["failed_files"])
            )

        return upload_results

    async def _sync_pending_files(
        self, local_files: Set[Tuple[str, int]], cloud_files: Set[Tuple[str, int]]
    ) -> Set[str]:
        local_files_dict = {name: size for name, size in local_files}
        cloud_files_dict = {name: size for name, size in cloud_files}
        uploading = set()
        for file_name, local_size in local_files_dict.items():
            if file_name not in cloud_files_dict:
                uploading.add(file_name)
            else:
                cloud_size = cloud_files_dict[file_name]
                if local_size != cloud_size:
                    uploading.add(file_name)
        return uploading

    async def _extract_thies_daily_statistics(self) -> None:
        daily_files = [
            prefix + datetime_to_str(today(), date_format="%Y%m%d") + ".BIN"
            for prefix in ["AVG_", "EXT_"]
        ]
        for file in daily_files:
            prefix, filename = file.split("_", 1)
            file_path = self.os_client.join_paths(
                self.local_backup_path, PostThiesDataUseCase.BASE_FOLDER_NAME, prefix
            )
            files = await self.os_client.listdir(file_path)
            if filename not in files:
                reason = "The file might not be available yet for statistics."
                self.logger.warning("[thies_synchronization_lib] Warning: %s", reason)
                self.logger.warning(
                    "[thies_synchronization_lib] Skipping the creation of daily statistics %s",
                    filename,
                )
                return
        await create_thies_daily_statistics_file(
            self.local_backup_path, self.os_client, self.logger
        )

    async def _validate_local_backup(self):
        backup_path = self.os_client.join_paths(
            self.local_backup_path, PostThiesDataUseCase.BASE_FOLDER_NAME
        )
        backup_dir_exists = await self.os_client.path_exists(backup_path)
        if not backup_dir_exists:
            await self.os_client.makedirs(backup_path)

        for dest_folder in {"AVG", "EXT"}:
            dest_folder_path = self.os_client.join_paths(backup_path, dest_folder)
            dest_folder_exists = await self.os_client.path_exists(dest_folder_path)
            if not dest_folder_exists:
                await self.os_client.makedirs(
                    self.os_client.join_paths(backup_path, dest_folder)
                )

    async def _fill_local_backup(self, thies_files: Set[Tuple[str, int]]) -> Set[str]:
        local_avg_files = await self.os_client.listdir(
            self.os_client.join_paths(
                self.local_backup_path, PostThiesDataUseCase.BASE_FOLDER_NAME, "AVG"
            ),
            more_info=True,
        )
        local_avg_files = {filename: size for filename, size in local_avg_files}
        local_ext_files = await self.os_client.listdir(
            self.os_client.join_paths(
                self.local_backup_path, PostThiesDataUseCase.BASE_FOLDER_NAME, "EXT"
            ),
            more_info=True,
        )
        local_ext_files = {filename: size for filename, size in local_ext_files}
        saved_files: Set[str] = set()
        try:
            for file, orig_size in thies_files:
                prefix, filename = file.split("_", 1)
                folder_path = next(
                    (
                        path
                        for path in self.ftp_server_folders_path
                        if prefix == ("AVG" if "AV" in path else "EXT")
                    ),
                    self.ftp_server_folders_path[0],
                )
                dest_path = self.os_client.join_paths(
                    self.local_backup_path,
                    PostThiesDataUseCase.BASE_FOLDER_NAME,
                    prefix,
                )
                new_size = (
                    local_avg_files.get(filename, None)
                    if prefix == "AVG"
                    else local_ext_files.get(filename, None)
                )
                should_be_added = False
                if new_size and new_size != orig_size:
                    should_be_added = True
                elif not new_size:
                    should_be_added = True

                if not should_be_added:
                    continue

                self.logger.debug(
                    f"[thies_synchronization_lib] Saving {filename} in Thies local backup"
                )
                file_path = f"{folder_path}/{filename}"
                if self.thies_ftp_client is None:
                    raise FtpClientError("FTP client was not initialized.")
                file_content = await self.thies_ftp_client.read_file(
                    FtpReadFileArgs(file_path)
                )
                await self.files_client.write(
                    WriteArgs(
                        file_name=filename,
                        file_content=file_content,
                        mode="wb",
                        destination_path=dest_path,
                    )
                )
                saved_files.add(file)
        except ConnectionRefusedError as error:
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            raise ThiesFetchingError(reason=error)

        return saved_files

    async def execute(self) -> Dict[str, Any]:
        self.logger.debug("[thies_synchronization_lib] Starting ...")
        if not self.need_to_backup and not self.need_to_sync:
            raise EmptyDataError(reason="No backup or sync requested.")

        try:
            await self._validate_local_backup()
        except OSError as error:
            raise BackupSourcePathError(reason=error)

        result: Dict[str, Any] = {
            "need_to_backup": self.need_to_backup,
            "need_to_sync": self.need_to_sync,
        }

        if self.need_to_backup:
            try:
                thies_files = await self.fetch_thies_file_names()
                backed_up_files = await self._fill_local_backup(thies_files)
            except RuntimeError as error:
                raise FtpClientError(error)
            await self._extract_thies_daily_statistics()
            result["backup"] = {
                "backed_up_files": sorted(backed_up_files),
                "total": len(backed_up_files),
            }

        if self.need_to_sync:
            try:
                local_files = await self.fetch_local_backup_file_names()
            except OSError as error:
                raise BackupSourcePathError(reason=error)
            try:
                cloud_files = await self.fetch_cloud_file_names()
            except (RuntimeError, ConnectionError) as error:
                raise SharepointClientError(error)

            self.uploading = await self._sync_pending_files(local_files, cloud_files)
            if self.uploading:
                local_backup_files = await self.fetch_local_backup_file_content()
                upload_statistics = await self.upload_thies_files_to_sharepoint(
                    local_backup_files
                )
                result["sync"] = parse_execute_response(
                    local_backup_files, upload_statistics
                )
            else:
                result["sync"] = {
                    "failed_files": [],
                    "new_files": [],
                    "processed_files": {},
                }

        return result
