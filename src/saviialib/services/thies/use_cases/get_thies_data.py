from saviialib.general_types.error_types.api.saviia_api_error_types import (
    SharePointFetchingError,
    ThiesConnectionError,
    ThiesFetchingError,
    BackupSourcePathError,
)
from saviialib.general_types.error_types.common import (
    FtpClientError,
    SharepointClientError,
)
from saviialib.libs.ftp_client import (
    FTPClient,
    FtpClientInitArgs,
    FtpListFilesArgs,
)
from saviialib.libs.sharepoint_client import (
    SharepointClient,
    SharepointClientInitArgs,
    SpListFilesArgs,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs

from saviialib.libs.log_client import (
    LogClient,
    LogClientArgs,
    LogStatus,
    DebugArgs,
    ErrorArgs,
    WarningArgs
)

from saviialib.libs.files_client import (
    FilesClient,
    FilesClientInitArgs,
)
from saviialib.services.backup.use_cases.types import (
    GetThiesDataUseCaseInput,
    GetThiesDataUseCaseOutput,
)


from typing import Set, Dict


class GetThiesDataUseCase:
    def __init__(self, input: GetThiesDataUseCaseInput):
        # Clients initialization
        self.sharepoint_client = SharepointClient(
            SharepointClientInitArgs(
                input.sharepoint_config, client_name="sharepoint_rest_api"
            )
        )
        self.thies_ftp_client = FTPClient(
            FtpClientInitArgs(input.ftp_config, client_name="ftplib_client")
        )
        self.files_client = FilesClient(
            FilesClientInitArgs(client_name="aiofiles_client")
        )
        self.dir_client = DirectoryClient(DirectoryClientArgs(client_name="os_client"))
        self.logger = LogClient(
            LogClientArgs("logging", service_name="thies", class_name="get_thies_data")
        )
        # Configurations

        self.local_backup_path = input.local_backup_path
        self.sharepoint_base_url = f"/sites/{self.sharepoint_client.site_name}"
        self.sync_error = False
        self.uploading = set()

    async def _fetch_local_backup_files(self) -> Dict[str, int | Set[str]]:
        backup_path_exists = await self.dir_client.path_exists(self.local_backup_path)
        if not backup_path_exists:
            raise BackupSourcePathError(
                reason=f"Local Backup path '{backup_path_exists}' doesn't exist"
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
        thies_avg_files = await self.dir_client.listdir(
            self.dir_client.join_paths(thies_backup_path, "AVG")
        )
        thies_ext_files = await self.dir_client.listdir(
            self.dir_client.join_paths(thies_backup_path, "EXT")
        )
        return {
            "filenames": set(thies_avg_files),
            "count_avg_files": len(thies_avg_files),
            "count_ext_files": len(thies_ext_files),
        }

    async def _fetch_cloud_total_files(self) -> Set[str]:
        """Fetch file names from the RCER cloud."""
        cloud_files = set()
        sharepoint_base_url = self.dir_client.join_paths(self.local_backup_path, 'thies')
        async with self.sharepoint_client:
            for folder_name in {"AVG", "EXT"}:
                relative_url = f"{sharepoint_base_url}/{folder_name}"
                args = SpListFilesArgs(folder_relative_url=relative_url)
                response = await self.sharepoint_client.list_files(args)
                cloud_files.update(
                    {
                        (f"{folder_name}_{item['Name']}", int(item["Length"]))
                        for item in response["value"]  # type: ignore
                    }  # type: ignore
                )
        return cloud_files
      

    async def _fetch_thies_total_files(self) -> Set[str]:
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
        thies_files: Set[str],
        cloud_files: Set[str],
        backup_files: Dict[str, Set[str] | int],
    ):
        """Review whether it is necessary to perform a new synchronisation or create a new backup
        from the FTP Server"""
        self.logger.method_name = "_validate_pending_files"
        self.logger.debug(DebugArgs(status=LogStatus.STARTED))
        thies_files_dict = {name: size for name, size in thies_files}
        cloud_files_dict = {name: size for name, size in cloud_files}
        unsynchronised_files, unbacked_files = set(), set()
        # Check out if it is need to execute a new backup
        if backup_files["count_ext_files"] != backup_files["count_avg_files"]:
            need_to_backup = True
        unbacked_files = thies_files.difference(backup_files["filenames"])  # type: ignore
        if len(unbacked_files) > 0:
            need_to_backup = True
        need_to_backup = True if len(unbacked_files) > 0 else False
        # Check out whether it should consider a new synchronisation
        if not self.sync_error:
            for f_from_thies, f_size_from_thies in thies_files_dict.items():
                # If is in thies but not in cloud, then upload it
                if f_from_thies not in cloud_files_dict:
                    unsynchronised_files.add(f_from_thies)
                else:
                    # If the file is in both services, but the size is different, then upload it
                    f_size_from_cloud = cloud_files_dict[f_from_thies]
                    if f_size_from_thies != f_size_from_cloud:
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
            "unbacked_files": unbacked_files,
            "unsynchronised_files": unsynchronised_files,
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
            self.logger.warning(
                WarningArgs(status=LogStatus.FAILED, metadata={"msg": error.__str__()})
            )
            # raise SharepointClientError(error)
        validation = self._validate_pending_files(
            thies_files, cloud_files, backup_files
        )
        return GetThiesDataUseCaseOutput(
            need_to_sync=validation["need_to_sync"],
            need_to_backup=validation["need_to_backup"],
            unbacked_files=validation["unbacked_files"],
            unsynchronised_files=validation["unsynchronised_files"],
        )
