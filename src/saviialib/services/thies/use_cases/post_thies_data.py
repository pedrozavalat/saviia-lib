import os

from typing import Any, Dict, List, Set, Tuple

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
    CloudClientFetchingError,
    CloudClientUploadError,
    ThiesConnectionError,
    ThiesFetchingError,
)
from saviialib.general_types.error_types.common import (
    EmptyDataError,
    FtpClientError,
    CloudClientError,
)
from saviialib.libs.files_client import (
    ReadArgs,
    WriteArgs,
)
from saviialib.libs.ftp_client import (
    FtpListFilesArgs,
    FtpReadFileArgs,
)
from saviialib.libs.cloud_client import (
    CloudClientListFilesArgs,
    CloudClientCreateFolderArgs,
    CloudClientUploadFileArgs,
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
from saviialib.services.thies.use_cases.utils.post_thies_data_utils import (
    parse_execute_response,
)
from saviialib.libs.log_client import (
    LogClient,
    LogClientArgs,
    LogStatus,
    DebugArgs,
    ErrorArgs,
    WarningArgs,
)


class PostThiesDataUseCase:
    BASE_FOLDER_NAME = "thies"

    def __init__(self, input: PostThiesDataUseCaseInput):
        self.need_to_sync = input.need_to_sync
        self.need_to_backup = input.need_to_backup
        self.cloud_client = input.cloud_client
        self.logger = input.logger
        self.log_client = LogClient(
            LogClientArgs(
                "logging",
                service_name="thies",
                class_name="post_thies_data",
                logger=input.logger,
            )
        )
        self.thies_ftp_client = input.ftp_client
        self.cloud_provider_destination_path = input.cloud_provider_destination_path
        self.ftp_server_folders_path = input.ftp_server_folders_path
        self.local_backup_path = input.local_backup_source_path
        self.uploading = set()
        self.os_client = input.directory_client
        self.files_client = input.files_client

    def _cloud_provider_thies_base_path(self) -> str:
        backup_root = self.os_client.get_basename(self.local_backup_path.rstrip("/"))

        return "/".join(
            [
                self.cloud_provider_destination_path.rstrip("/"),
                backup_root,
                PostThiesDataUseCase.BASE_FOLDER_NAME,
            ]
        )

    @staticmethod
    def _extract_local_entry(entry) -> tuple[str, int | None]:
        if isinstance(entry, tuple):
            name = entry[0]
            size = entry[1] if len(entry) > 1 else None
            return name, int(size) if size is not None else None
        return entry, None

    async def _validate_sharepoint_destination(self):
        self.log_client.method_name = "_validate_sharepoint_destination"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))
        if self.cloud_client is None:
            raise CloudClientError("Cloud Client was not initialized.")

        async with self.cloud_client:
            cloud_provider_thies_path = self._cloud_provider_thies_base_path()
            await self.cloud_client.create_folder(
                CloudClientCreateFolderArgs(
                    folder_relative_url=cloud_provider_thies_path,
                )
            )
            for folder_name in {"AVG", "EXT"}:
                await self.cloud_client.create_folder(
                    CloudClientCreateFolderArgs(
                        folder_relative_url=f"{cloud_provider_thies_path}/{folder_name}",
                    )
                )
        self.log_client.debug(DebugArgs(status=LogStatus.SUCCESSFUL))

    async def fetch_cloud_file_names(self) -> Set[Tuple[str, int]]:
        self.log_client.method_name = "fetch_cloud_file_names"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))
        if self.cloud_client is None:
            raise CloudClientError("SAVIIA Cloud Client provider was not initialized.")

        await self._validate_sharepoint_destination()
        try:
            cloud_files: Set[Tuple[str, int]] = set()
            async with self.cloud_client:
                cloud_provider_thies_path = self._cloud_provider_thies_base_path()
                for folder_name in {"AVG", "EXT"}:
                    relative_url = f"{cloud_provider_thies_path}/{folder_name}"

                    args = CloudClientListFilesArgs(folder_relative_url=relative_url)
                    response = await self.cloud_client.list_files(args)
                    entries = [
                        (item["name"], int(item.get("file_size", 0)))
                        for item in response
                        if not item.get("is_directory", False)
                    ]
                    cloud_files.update(
                        (f"{folder_name}_{name}", size) for name, size in entries
                    )
            self.log_client.debug(
                DebugArgs(
                    status=LogStatus.SUCCESSFUL,
                    metadata={"msg": f"Fetched {len(cloud_files)} cloud files"},
                )
            )
            return cloud_files
        except Exception as error:
            self.log_client.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            raise CloudClientFetchingError(reason=error)

    async def fetch_thies_file_names(self) -> Set[Tuple[str, int]]:
        self.log_client.method_name = "fetch_thies_file_names"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))
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
            self.log_client.debug(
                DebugArgs(
                    status=LogStatus.SUCCESSFUL,
                    metadata={"msg": f"Fetched {len(thies_files)} THIES files"},
                )
            )
            return thies_files
        except ConnectionRefusedError as error:
            self.log_client.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            self.log_client.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            raise ThiesFetchingError(reason=error)

    async def fetch_local_backup_file_names(self) -> Set[Tuple[str, int]]:
        self.log_client.method_name = "fetch_local_backup_file_names"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))
        avg_folder_path = self.os_client.join_paths(
            self.local_backup_path, PostThiesDataUseCase.BASE_FOLDER_NAME, "AVG"
        )
        ext_folder_path = self.os_client.join_paths(
            self.local_backup_path, PostThiesDataUseCase.BASE_FOLDER_NAME, "EXT"
        )
        thies_avg_files = await self.os_client.listdir(avg_folder_path)
        thies_ext_files = await self.os_client.listdir(ext_folder_path)
        avg_entries = []
        for entry in thies_avg_files:
            filename, entry_size = self._extract_local_entry(entry)
            file_path = self.os_client.join_paths(avg_folder_path, filename)
            if await self.os_client.isdir(file_path):
                continue
            avg_entries.append(
                (
                    filename,
                    entry_size
                    if entry_size is not None
                    else os.path.getsize(file_path),
                )
            )
        ext_entries = []
        for entry in thies_ext_files:
            filename, entry_size = self._extract_local_entry(entry)
            file_path = self.os_client.join_paths(ext_folder_path, filename)
            if await self.os_client.isdir(file_path):
                continue
            ext_entries.append(
                (
                    filename,
                    entry_size
                    if entry_size is not None
                    else os.path.getsize(file_path),
                )
            )
        local_files = {
            *((f"AVG_{filename}", size) for filename, size in avg_entries),
            *((f"EXT_{filename}", size) for filename, size in ext_entries),
        }
        self.log_client.debug(
            DebugArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={"msg": f"Fetched {len(local_files)} local backup files"},
            )
        )
        return local_files

    async def fetch_local_backup_file_content(self) -> Dict[str, bytes]:
        self.log_client.method_name = "fetch_local_backup_file_content"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))
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
                self.log_client.debug(
                    DebugArgs(
                        status=LogStatus.SUCCESSFUL,
                        metadata={
                            "msg": f"Reading local file '{file}' from '{file_path}'"
                        },
                    )
                )
                content_files[file] = content
            self.log_client.debug(
                DebugArgs(
                    status=LogStatus.SUCCESSFUL,
                    metadata={"msg": f"Loaded content for {len(content_files)} files"},
                )
            )
            return content_files
        except ConnectionRefusedError as error:
            self.log_client.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            self.log_client.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            raise ThiesFetchingError(reason=error)

    async def upload_thies_files_to_cloud(
        self, files: Dict[str, bytes]
    ) -> Dict[str, List[str]]:
        self.log_client.method_name = "upload_thies_files_to_cloud"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))
        if self.cloud_client is None:
            raise CloudClientError("SAVIIA Cloud client provider was not initialized.")

        upload_results = {"failed_files": [], "new_files": []}

        async with self.cloud_client:
            sharepoint_thies_path = self._cloud_provider_thies_base_path()
            for file, file_content in files.items():
                try:
                    origin, file_name = file.split("_", 1)
                    folder_path = f"{sharepoint_thies_path}/{origin}"
                    # Avoid duplicating the site prefix: if folder_path already
                    # contains the site base, use it directly; otherwise prefix it.
                    relative_url = folder_path
                    # Log the resolved SAVIIA Cloud Provider  relative URL for diagnostics
                    self.log_client.debug(
                        DebugArgs(
                            status=LogStatus.STARTED,
                            metadata={
                                "msg": f"Resolved SAVIIA Cloud provider URL: {relative_url}"
                            },
                        )
                    )
                    await self.cloud_client.upload_file(
                        CloudClientUploadFileArgs(
                            folder_relative_url=relative_url,
                            file_content=file_content,
                            file_name=file_name,
                        )
                    )
                    upload_results["new_files"].append(file)
                    self.log_client.debug(
                        DebugArgs(
                            status=LogStatus.SUCCESSFUL,
                            metadata={
                                "msg": f"Uploaded '{file_name}' to '{relative_url}'"
                            },
                        )
                    )
                except ConnectionError as error:
                    self.log_client.error(
                        ErrorArgs(
                            status=LogStatus.ERROR,
                            metadata={
                                "msg": f"Failed uploading '{file_name}': {str(error)}"
                            },
                        )
                    )
                    upload_results["failed_files"].append(
                        f"{file} (Error: {str(error)})"
                    )

        if upload_results["failed_files"]:
            raise CloudClientUploadError(
                reason="Files failed to upload: "
                + ", ".join(upload_results["failed_files"])
            )

        self.log_client.debug(
            DebugArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={"msg": f"Uploaded {len(upload_results['new_files'])} files"},
            )
        )
        return upload_results

    async def _sync_pending_files(
        self, local_files: Set[Tuple[str, int]], cloud_files: Set[Tuple[str, int]]
    ) -> Set[str]:
        self.log_client.method_name = "_sync_pending_files"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))
        local_files_dict = {name: size for name, size in local_files}
        cloud_files_dict = {name: size for name, size in cloud_files}
        uploading = set()
        for file_name, local_size in local_files_dict.items():
            if file_name not in cloud_files_dict:
                uploading.add(file_name)
            else:
                cloud_size = cloud_files_dict[file_name]
                # Treat zero-size readings as unknown metadata and do not force a resync.
                if local_size > 0 and cloud_size > 0 and local_size != cloud_size:
                    uploading.add(file_name)
        self.log_client.debug(
            DebugArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={"msg": f"Pending files to upload: {len(uploading)}"},
            )
        )
        return uploading

    async def _extract_thies_daily_statistics(self) -> None:
        self.log_client.method_name = "_extract_thies_daily_statistics"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))
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
                self.log_client.warning(
                    WarningArgs(status=LogStatus.FAILED, metadata={"msg": reason})
                )
                self.log_client.warning(
                    WarningArgs(
                        status=LogStatus.FAILED,
                        metadata={
                            "msg": f"Skipping daily statistics creation for '{filename}'"
                        },
                    )
                )
                return
        await create_thies_daily_statistics_file(
            self.local_backup_path, self.os_client, self.logger
        )
        self.log_client.debug(DebugArgs(status=LogStatus.SUCCESSFUL))

    async def _validate_local_backup(self):
        self.log_client.method_name = "_validate_local_backup"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))
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
        self.log_client.debug(DebugArgs(status=LogStatus.SUCCESSFUL))

    async def _fill_local_backup(self, thies_files: Set[Tuple[str, int]]) -> Set[str]:
        self.log_client.method_name = "_fill_local_backup"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))
        avg_folder_path = self.os_client.join_paths(
            self.local_backup_path, PostThiesDataUseCase.BASE_FOLDER_NAME, "AVG"
        )
        ext_folder_path = self.os_client.join_paths(
            self.local_backup_path, PostThiesDataUseCase.BASE_FOLDER_NAME, "EXT"
        )
        local_avg_files = {}
        for entry in await self.os_client.listdir(avg_folder_path):
            filename, entry_size = self._extract_local_entry(entry)
            file_path = self.os_client.join_paths(avg_folder_path, filename)
            if await self.os_client.isdir(file_path):
                continue
            local_avg_files[filename] = (
                entry_size if entry_size is not None else os.path.getsize(file_path)
            )
        local_ext_files = {}
        for entry in await self.os_client.listdir(ext_folder_path):
            filename, entry_size = self._extract_local_entry(entry)
            file_path = self.os_client.join_paths(ext_folder_path, filename)
            if await self.os_client.isdir(file_path):
                continue
            local_ext_files[filename] = (
                entry_size if entry_size is not None else os.path.getsize(file_path)
            )
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

                self.log_client.debug(
                    DebugArgs(
                        status=LogStatus.SUCCESSFUL,
                        metadata={"msg": f"Saving '{filename}' to local backup"},
                    )
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
            self.log_client.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            raise ThiesConnectionError(reason=error)
        except ConnectionAbortedError as error:
            self.log_client.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            raise ThiesFetchingError(reason=error)

        self.log_client.debug(
            DebugArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={"msg": f"Backed up {len(saved_files)} files"},
            )
        )
        return saved_files

    async def execute(self) -> Dict[str, Any]:
        self.log_client.method_name = "execute"
        self.log_client.debug(DebugArgs(status=LogStatus.STARTED))

        if not self.need_to_backup and not self.need_to_sync:
            self.log_client.warning(
                WarningArgs(
                    status=LogStatus.FAILED,
                    metadata={"msg": "No backup or sync requested"},
                )
            )
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
                self.log_client.error(
                    ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
                )
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
                raise CloudClientError(error)

            self.uploading = await self._sync_pending_files(local_files, cloud_files)
            if self.uploading:
                local_backup_files = await self.fetch_local_backup_file_content()
                upload_statistics = await self.upload_thies_files_to_cloud(
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

        self.log_client.debug(
            DebugArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={
                    "msg": (
                        f"Completed post_thies_data. "
                        f"backup={self.need_to_backup}, sync={self.need_to_sync}"
                    )
                },
            )
        )
        return result
