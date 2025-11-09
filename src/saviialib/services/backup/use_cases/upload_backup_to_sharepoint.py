import asyncio
from time import time
from logging import Logger
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupEmptyError,
    BackupSourcePathError,
    BackupUploadError,
)
from saviialib.general_types.error_types.common import (
    SharepointClientError,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.files_client import (
    FilesClient,
    FilesClientInitArgs,
    ReadArgs,
    WriteArgs,
)
from saviialib.libs.sharepoint_client import (
    SharepointClient,
    SharepointClientInitArgs,
    SpUploadFileArgs,
    SpCreateFolderArgs,
    SpListFilesArgs,
)
from saviialib.libs.log_client import (
    LogClient,
    LogClientArgs,
    InfoArgs,
    DebugArgs,
    WarningArgs,
    ErrorArgs,
    LogStatus,
)

from saviialib.services.backup.utils.upload_backup_to_sharepoint_utils import (
    calculate_percentage_uploaded,
    count_files_in_directory,
    parse_execute_response,
    show_upload_result,
)

from .types.upload_backup_to_sharepoint_types import (
    UploadBackupToSharepointUseCaseInput,
)
from typing import Dict, List


class UploadBackupToSharepointUsecase:
    LOCAL_BACKUP_NAME = "saviia-local-backup"

    def __init__(self, input: UploadBackupToSharepointUseCaseInput):
        self.sharepoint_config = input.sharepoint_config
        self.local_backup_source_path = input.local_backup_source_path
        self.sharepoint_destination_path = input.sharepoint_destination_path
        self.files_client = self._initialize_files_client()
        self.dir_client = self._initialize_directory_client()
        self.sharepoint_client = self._initalize_sharepoint_client()

        self.grouped_files_by_folder = {}
        self.logger: Logger = input.logger
        self.infofile: Dict[str, str | List[str]] = {}
        self.log_client = LogClient(
            LogClientArgs(
                client_name="logging",
                class_name="backup_to_sharepoint",
                service_name="backup",
                active_record=True,
            )
        )

    def _initalize_sharepoint_client(self):
        return SharepointClient(
            SharepointClientInitArgs(
                self.sharepoint_config, client_name="sharepoint_rest_api"
            )
        )

    def _initialize_directory_client(self):
        return DirectoryClient(DirectoryClientArgs(client_name="os_client"))

    def _initialize_files_client(self):
        return FilesClient(FilesClientInitArgs(client_name="aiofiles_client"))

    async def _group_files_by_folder(self) -> dict[str, list[str]]:
        """Groups files to upload by their parent folder"""
        folder_names = await self.dir_client.listdir(self.local_backup_source_path)
        grouped = {}
        if len(folder_names) == 0:
            raise BackupEmptyError
        for folder_name in folder_names:
            is_folder = await self.dir_client.isdir(
                self.dir_client.join_paths(self.local_backup_source_path, folder_name)
            )
            if not is_folder:
                continue
            grouped[folder_name] = await self.dir_client.listdir(
                self.dir_client.join_paths(self.local_backup_source_path, folder_name)
            )
            grouped[folder_name] = set(grouped[folder_name])
        return grouped

    async def _create_or_update_infofile(self):
        """Function that creates or update the information JSON file, which contains status flags
        for each directory."""
        self.log_client.method_name = "_create_or_update_infofile"
        infofile_path = self.dir_client.join_paths(
            self.local_backup_source_path, ".infofile.json"
        )  # type: ignore
        infofile_exists = await self.dir_client.path_exists(infofile_path)
        if infofile_exists:
            self.log_client.debug(
                DebugArgs(LogStatus.ALERT, metadata={"msg": "Creating .infofile.json"})
            )
            self.infofile = await self.files_client.read(
                ReadArgs(file_path=infofile_path, mode="json")
            )  # type: ignore
        else:
            self.log_client.debug(
                DebugArgs(LogStatus.ALERT, metadata={"msg": "Updating .infofile.json"})
            )
            for folder, files in self.grouped_files_by_folder.items():  # type: ignore
                should_pass = (
                    True
                    if len(list(filter(lambda f: f == ".PASS.txt", files))) > 0
                    else False
                )
                should_reset = (
                    True
                    if len(list(filter(lambda f: f == ".RESET.txt", files))) > 0
                    else False
                )
                self.infofile[folder] = {  # type: ignore
                    "pass": should_pass,
                    "reset": should_reset,
                    "failed": [],
                }

    async def prepare_backup(self):
        self.log_client.method_name = "prepare_backup"
        self.log_client.debug(
            DebugArgs(
                LogStatus.STARTED,
                metadata={"msg": "* Extracting folders from local backup directory *"},
            )
        )
        # Check if the local backup directory exists. If doesn't exist, then create it.
        local_backup_path_exists = await self.dir_client.path_exists(
            self.local_backup_source_path
        )
        if not local_backup_path_exists:
            raise BackupSourcePathError(
                reason=f"'{self.local_backup_source_path}' doesn't exist."
            )
        # Create the destination directory if it doesn't exist
        complete_destination_path = (
            self.sharepoint_destination_path
            + "/"
            + UploadBackupToSharepointUsecase.LOCAL_BACKUP_NAME
        )
        async with self.sharepoint_client:
            await self.sharepoint_client.create_folder(
                SpCreateFolderArgs(folder_relative_url=complete_destination_path)
            )
        # Check out the directories and the files inside each one
        self.grouped_files_by_folder = await self._group_files_by_folder()
        # Create or read the info file
        await self._create_or_update_infofile()
        # Replicate local directories in the sharepoint directory.
        for folder in self.grouped_files_by_folder.keys():
            should_pass = self.infofile[folder]["pass"]  # type: ignore
            should_reset = self.infofile[folder]["reset"]  # type: ignore
            if should_reset:
                self.log_client.warning(
                    WarningArgs(
                        LogStatus.ALERT,
                        metadata={
                            "msg": f"The '{folder}' will reseted before the synchronization as it contains the .RESET.txt file ❗️"
                        },
                    )
                )
            if should_pass:
                self.log_client.debug(
                    DebugArgs(
                        LogStatus.ALERT,
                        metadata={
                            "msg": f"The '{folder}' will not be synchronised as it contains the .PASS.txt file 👻"
                        },
                    )
                )
                continue
            async with self.sharepoint_client:
                await self.sharepoint_client.create_folder(
                    SpCreateFolderArgs(
                        folder_relative_url=complete_destination_path + "/" + folder
                    )
                )
            self.grouped_files_by_folder[folder] = set(
                self.grouped_files_by_folder[folder]
            ) - {".PASS.txt", ".RESET.txt"}  # type: ignore
        self.sharepoint_destination_path = complete_destination_path

        self.log_client.debug(
            DebugArgs(LogStatus.SUCCESSFUL, metadata={"msg": "Ready to migrate"})
        )

    async def migrate_files(self) -> list:
        self.log_client.method_name = "migrate_files"
        self.log_client.debug(
            DebugArgs(
                LogStatus.STARTED, metadata={"msg": "* Counting files to migrate *"}
            )
        )
        tasks = []
        local_files: set
        for folder_name, local_files in self.grouped_files_by_folder.items():  # type: ignore
            should_pass = self.infofile[folder_name]["pass"]  # type: ignore
            if should_pass:
                continue

            count_files_in_dir = await count_files_in_directory(
                self.local_backup_source_path, folder_name
            )
            if count_files_in_dir == 0:
                self.log_client.debug(
                    DebugArgs(
                        LogStatus.ALERT,
                        metadata={"msg": f"The folder '{folder_name}' is empty ⚠️"},
                    )
                )
                continue
            # Check out the pending files and add the failed failes
            self.log_client.debug(
                DebugArgs(
                    LogStatus.ALERT,
                    metadata={
                        "msg": f"Checking files to upload in '{folder_name}' directory 👀"
                    },
                )
            )
            async with self.sharepoint_client:
                files = await self.sharepoint_client.list_files(
                    SpListFilesArgs(
                        self.sharepoint_destination_path + "/" + folder_name
                    )
                )
                sharepoint_files = {x["Name"] for x in files["value"]}  # type: ignore
                failed_files = set(self.infofile[folder_name]["failed"])  # type: ignore
                pending_files = local_files.difference(sharepoint_files)
                pending_files = pending_files.union(failed_files)
                summary_msg = (
                    f"Sharepoint Files: {len(sharepoint_files)}. "
                    f"Local Files: {len(local_files)}. "
                    f"Failed files: {len(failed_files)}. "
                    f"Pending Files: {len(pending_files)}. "
                )
                self.log_client.debug(
                    DebugArgs(
                        LogStatus.ALERT,
                        metadata={"msg": summary_msg},
                    )
                )

                # Update the files to upload
                self.grouped_files_by_folder[folder_name] = list(pending_files)  # type: ignore
                if len(pending_files) == 0:
                    self.log_client.debug(
                        DebugArgs(
                            LogStatus.ALERT,
                            metadata={
                                "msg": f"All the files in '{folder_name}' have already been synchronised"
                            },
                        )
                    )
                    continue
            # Export the file to Sharepoint
            for file_name in self.grouped_files_by_folder[folder_name]:  # type: ignore
                if file_name in [".RESET.txt", ".PASS.txt"]:
                    continue
                tasks.append(self._upload_file_to_sharepoint(folder_name, file_name))
        self.log_client.debug(
            DebugArgs(
                LogStatus.SUCCESSFUL,
                metadata={"msg": "* The reviewing process has finished *"},
            )
        )
        return tasks

    async def _upload_file_to_sharepoint(self, folder_name, file_name) -> dict:
        """Task for uploads a file and logs progress."""
        self.log_client.method_name = "_upload_file_to_sharepoint"
        self.log_client.debug(
            DebugArgs(
                LogStatus.STARTED,
                metadata={"msg": f"Uploading file '{file_name}' from '{folder_name}' "},
            )
        )
        # Retrieve the content from the file in the local directory
        file_path = self.dir_client.join_paths(
            self.local_backup_source_path, folder_name, file_name
        )
        file_content = await self.files_client.read(ReadArgs(file_path, mode="rb"))
        # Upload the local file to Sharepoint directory
        uploaded, error_message = None, ""
        try:
            sharepoint_client = SharepointClient(
                SharepointClientInitArgs(
                    self.sharepoint_config, client_name="sharepoint_rest_api"
                )
            )
        except ConnectionError as error:
            self.log_client.error(
                ErrorArgs(
                    LogStatus.ERROR,
                    metadata={"msg": error.__str__()},
                )
            )
            raise SharepointClientError(error)
        async with sharepoint_client:
            try:
                folder_url = f"{self.sharepoint_destination_path}/{folder_name}"
                args = SpUploadFileArgs(
                    folder_relative_url=folder_url,
                    file_content=file_content,  # type: ignore
                    file_name=file_name,
                )
                await sharepoint_client.upload_file(args)
                uploaded = True
                # Remove the file from the source directory if RESET is true
                should_reset = self.infofile[folder_name]["reset"]  # type: ignore
                if should_reset:
                    source_file_path = self.dir_client.join_paths(
                        self.local_backup_source_path, folder_name, file_name
                    )
                    await self.dir_client.remove_file(source_file_path)
                    self.log_client.debug(
                        DebugArgs(
                            LogStatus.ALERT,
                            metadata={
                                "msg": f"File {file_name} has been deleted from '{folder_name}'"
                            },
                        )
                    )
            except ConnectionError as error:
                error_message = str(error)
                uploaded = False
                # Add the file to failed failes
                self.infofile[folder_name]["failed"].append(file_name)  # type: ignore
        self.log_client.debug(
            DebugArgs(
                LogStatus.SUCCESSFUL if uploaded else LogStatus.ALERT,
                metadata={
                    "msg": show_upload_result(uploaded, file_name, error_message)
                },
            )
        )
        return {
            "parent_folder": folder_name,
            "file_name": file_name,
            "uploaded": uploaded,
            "error_message": error_message,
        }

    async def _save_log_history(self) -> None:
        await self.files_client.write(
            WriteArgs(
                file_name="BACKUP_LOG_HISTORY.log",
                file_content="\n".join(self.log_client.log_history),
                mode="w",
            )
        )

    async def execute(self):
        """Exports all files from the local backup folder to SharePoint cloud."""
        self.log_client.method_name = "execute"
        self.log_client.info(
            InfoArgs(LogStatus.STARTED, metadata={"msg": "Starting backup process"})
        )
        start_time = time()
        await self.prepare_backup()
        tasks = await self.migrate_files()
        already_migrated = (
            len(tasks) == 0
        )  # If the tasks set is zero, then were no any errors.
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = calculate_percentage_uploaded(results, len(tasks))  # type: ignore
        if success < 100.0 and not already_migrated:
            self.log_client.method_name = "execute"
            self.log_client.warning(
                WarningArgs(
                    LogStatus.FAILED,
                    metadata={
                        "msg": (
                            "Not all the files have been uploaded ⚠️."
                            f"Files failed to upload: {(1 - success):.2%}"
                        )
                    },
                )
            )
            # Save any failed files for exporting in the next migration
            await self.files_client.write(
                WriteArgs(
                    file_name=".infofile.json",
                    file_content=self.infofile,  # type: ignore
                    mode="json",
                )
            )
        else:
            end_time = time()
            backup_time = end_time - start_time
            self.log_client.method_name = "execute"
            self.log_client.debug(
                DebugArgs(
                    LogStatus.SUCCESSFUL,
                    metadata={
                        "msg": (
                            f"Migration time: {backup_time:.2f} seconds ✨. "
                            "All the files were uploaded successfully 🎉"
                        )
                    },
                )
            )
            await self._save_log_history()
            return parse_execute_response(results)  # type: ignore
