import os

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ThiesFetchingError,
    BackupSourcePathError,
)
from saviialib.general_types.error_types.common import (
    FtpClientError,
)
from saviialib.libs.ftp_client import (
    FtpListFilesArgs,
)
from saviialib.libs.cloud_client import (
    CloudClientListFilesArgs,
    CloudClientResolveUrlArgs,
)

from saviialib.libs.log_client import (
    LogClient,
    LogClientArgs,
    LogStatus,
    DebugArgs,
    ErrorArgs,
    WarningArgs,
)
from saviialib.services.thies.use_cases.types.get_thies_data_types import (
    GetThiesDataUseCaseInput,
    GetThiesDataUseCaseOutput,
)


from typing import Set, Dict, Mapping, cast


class GetThiesDataUseCase:
    def __init__(self, input: GetThiesDataUseCaseInput):
        # Clients initialization
        self.cloud_client = input.cloud_client
        self.thies_ftp_client = input.ftp_client
        self.files_client = input.files_client
        self.dir_client = input.directory_client
        self.logger = LogClient(
            LogClientArgs(
                "logging",
                service_name="thies",
                class_name="get_thies_data",
                logger=input.logger,
            )
        )
        # Configurations

        self.local_backup_path = input.local_backup_path
        self.cloud_provider_destination_path = input.cloud_provider_destination_path
        self.cloud_base_path = "/".join(
            [
                self.cloud_provider_destination_path.rstrip("/"),
                self.local_backup_path,
                "thies",
            ]
        )
        self.sync_error = False
        self.uploading = set()

    async def _list_local_files_with_sizes(
        self, folder_path: str
    ) -> list[tuple[str, int]]:
        filenames = await self.dir_client.listdir(folder_path)
        file_sizes: list[tuple[str, int]] = []
        for filename in filenames:
            file_path = self.dir_client.join_paths(folder_path, filename)
            if await self.dir_client.isdir(file_path):
                continue
            size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            file_sizes.append((filename, int(size)))
        return file_sizes

    async def _fetch_local_backup_files(
        self,
    ) -> Dict[str, int | Set[str] | Dict[str, int]]:
        backup_path_exists = await self.dir_client.path_exists(self.local_backup_path)
        if not backup_path_exists:
            raise BackupSourcePathError(
                reason=f"Local Backup path '{self.local_backup_path}' doesn't exist"
            )
        # Review if the /thies dir exists. In another case, create it.
        thies_backup_path = self.dir_client.join_paths(self.local_backup_path, "thies")
        thies_dir_exists = await self.dir_client.path_exists(thies_backup_path)
        if not thies_dir_exists:
            await self.dir_client.makedirs(thies_backup_path)
        # Create, if it don't exists, both directories AVG and EXT
        for dest_folder in {"AVG", "EXT"}:
            dest_folder_path = self.dir_client.join_paths(
                thies_backup_path, dest_folder
            )
            dest_folder_exists = await self.dir_client.path_exists(dest_folder_path)
            if not dest_folder_exists:
                await self.dir_client.makedirs(
                    self.dir_client.join_paths(thies_backup_path, dest_folder)
                )
        # Generate list of names and return it
        avg_folder_path = self.dir_client.join_paths(thies_backup_path, "AVG")
        ext_folder_path = self.dir_client.join_paths(thies_backup_path, "EXT")
        avg_entries = await self._list_local_files_with_sizes(avg_folder_path)
        ext_entries = await self._list_local_files_with_sizes(ext_folder_path)
        thies_avg_files = [name for name, _ in avg_entries]
        thies_ext_files = [name for name, _ in ext_entries]
        prefixed_avg = {f"AVG_{name}" for name, _ in avg_entries}
        prefixed_ext = {f"EXT_{name}" for name, _ in ext_entries}
        file_sizes = {f"AVG_{name}": size for name, size in avg_entries}
        file_sizes.update({f"EXT_{name}": size for name, size in ext_entries})
        return {
            "filenames": prefixed_avg.union(prefixed_ext),
            "file_sizes": file_sizes,
            "count_avg_files": len(thies_avg_files),
            "count_ext_files": len(thies_ext_files),
        }

    async def _fetch_cloud_total_files(self) -> Set[tuple[str, int]]:
        """Fetch file names from the RCER cloud."""
        cloud_files = set()
        if not self.cloud_provider_destination_path:
            raise BackupSourcePathError(
                reason="Cloud provider destination path is not configured"
            )
        async with self.cloud_client:
            for folder_name in {"AVG", "EXT"}:
                destination_folder_path = f"{self.cloud_base_path}/{folder_name}"
                relative_url = self.cloud_client.resolve_url(
                    CloudClientResolveUrlArgs(
                        folder_path=destination_folder_path
                    )
                )
                response = await self.cloud_client.list_files(
                    CloudClientListFilesArgs(folder_relative_url=relative_url)
                )
                entries = [
                    (item["name"], int(item.get("file_size", 0)))
                    for item in response
                    if not item.get("is_directory", False)
                ]
                cloud_files.update(
                    {
                        (f"{folder_name}_{item[0]}", item[1])
                        for item in entries
                    }  # type: ignore
                )
        return cloud_files

    async def _fetch_thies_total_files(self) -> Set[tuple[str, int]]:
        """Fetch file names from the THIES FTP server."""
        try:
            thies_files = set()
            for folder_path in {"/ARCH_AV1", "/ARCH_EX1"}:
                # AV for average, and EXT for extreme.
                prefix = "AVG" if "AV" in folder_path else "EXT"
                files = await self.thies_ftp_client.list_files(
                    FtpListFilesArgs(path=folder_path)
                )
                files_names = {(f"{prefix}_{name}", size) for name, size in files}
                thies_files.update(files_names)
            return thies_files
        except (ConnectionRefusedError, ConnectionAbortedError) as error:
            raise ThiesFetchingError(reason=error)

    def _validate_pending_files(
        self,
        thies_files: Set[tuple[str, int]],
        cloud_files: Set[tuple[str, int]],
        backup_files: Mapping[str, object],
    ):
        """Review whether it is necessary to perform a new synchronisation or create a new backup
        from the FTP Server"""
        self.logger.method_name = "_validate_pending_files"
        self.logger.debug(DebugArgs(status=LogStatus.STARTED))
        thies_files_dict = {name: int(size) for name, size in thies_files}
        cloud_files_dict = {name: int(size) for name, size in cloud_files}
        unsynchronised_files, unbacked_files = set(), set()
        # Check out if it is need to execute a new backup
        need_to_backup = False
        thies_file_names = {name for name, _ in thies_files}
        backup_filenames = cast(Set[str], backup_files["filenames"])
        backup_file_sizes = cast(Dict[str, int], backup_files.get("file_sizes", {}))
        count_ext_files = cast(int, backup_files.get("count_ext_files", 0))
        count_avg_files = cast(int, backup_files.get("count_avg_files", 0))
        if count_ext_files != count_avg_files:
            need_to_backup = True
        unbacked_files = thies_file_names.difference(backup_filenames)
        if len(unbacked_files) > 0:
            need_to_backup = True
        for file_name, thies_size in thies_files_dict.items():
            if (
                file_name in backup_file_sizes
                and backup_file_sizes[file_name] != thies_size
            ):
                need_to_backup = True
                unbacked_files.add(file_name)
        # Check out whether it should consider a new synchronisation
        if not self.sync_error:
            for f_from_thies, f_size_from_thies in thies_files_dict.items():
                # If is in thies but not in cloud, then upload it
                if f_from_thies not in cloud_files_dict:
                    unsynchronised_files.add(f_from_thies)
                else:
                    # If the file is in both services, but the size is different, then upload it
                    f_size_from_cloud = cloud_files_dict[f_from_thies]
                    # Treat zero-size readings as unknown metadata and do not force a resync.
                    if (
                        f_size_from_thies > 0
                        and f_size_from_cloud > 0
                        and f_size_from_thies != f_size_from_cloud
                    ):
                        unsynchronised_files.add(f_from_thies)
        need_to_sync = True if len(unsynchronised_files) > 0 else False
        self.logger.debug(
            DebugArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={
                    "msg": f"Backup?: {need_to_backup}. Synchronise?: {need_to_sync}"
                },
            )
        )
        self.logger.debug(
            DebugArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={"msg": f"Unbacked files: {unbacked_files}"},
            )
        )
        self.logger.debug(
            DebugArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={"msg": f"Unsynchronised files: {unsynchronised_files}"},
            )
        )
        return {
            "need_to_backup": need_to_backup,
            "need_to_sync": need_to_sync,
            "total_to_backup": len(unbacked_files),
            "total_to_sync": len(unsynchronised_files),
        }

    async def execute(self) -> GetThiesDataUseCaseOutput:
        """Synchronize data from the THIES Center to the cloud."""
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(status=LogStatus.STARTED))

        try:
            backup_files = await self._fetch_local_backup_files()
        except OSError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            raise BackupSourcePathError(reason=error)
        try:
            thies_files = await self._fetch_thies_total_files()
        except RuntimeError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            raise FtpClientError(error)
        try:
            cloud_files = await self._fetch_cloud_total_files()
        except (RuntimeError, ConnectionError) as error:
            self.sync_error = True
            cloud_files = set()
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            # raise SharepointClientError(error)
        validation = self._validate_pending_files(
            thies_files, cloud_files, backup_files
        )
        return GetThiesDataUseCaseOutput(
            need_to_sync=validation["need_to_sync"],
            need_to_backup=validation["need_to_backup"],
            total_to_backup=validation["total_to_backup"],
            total_to_sync=validation["total_to_sync"],
        )
