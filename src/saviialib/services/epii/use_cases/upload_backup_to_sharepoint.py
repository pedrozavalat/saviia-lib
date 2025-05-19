import asyncio
from time import time
from logging import Logger
from saviialib.general_types.error_types.api.epii_api_error_types import (
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
    SpListFoldersArgs,
)
from saviialib.services.epii.utils.upload_backup_to_sharepoint_utils import (
    calculate_percentage_uploaded,
    count_files_in_directory,
    extract_error_message,
    parse_execute_response,
    show_upload_result,
)

from .types.upload_backup_to_sharepoint_types import (
    UploadBackupToSharepointUseCaseInput,
)


class UploadBackupToSharepointUsecase:
    def __init__(self, input: UploadBackupToSharepointUseCaseInput):
        self.sharepoint_config = input.sharepoint_config
        self.local_backup_source_path = input.local_backup_source_path
        self.sharepoint_destination_path = input.sharepoint_destination_path
        self.files_client = self._initialize_files_client()
        self.dir_client = self._initialize_directory_client()
        self.log_history = []
        self.grouped_files_by_folder = None
        self.total_files = None
        self.logger: Logger = input.logger
        self.sharepoint_client = self._initalize_sharepoint_client()

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

    async def _validate_backup_structure(self):
        # Check if the local path exists in the main directory
        if not await self.dir_client.path_exists(self.local_backup_source_path):
            raise BackupSourcePathError(
                reason=f"'{self.local_backup_source_path}' doesn't exist."
            )

        local_directories = (
            list(self.grouped_files_by_folder.keys())
            if self.grouped_files_by_folder
            else []
        )
        async with self.sharepoint_client:  # type: ignore
            response = await self.sharepoint_client.list_folders(
                SpListFoldersArgs(folder_relative_url=self.sharepoint_destination_path)
            )
            sharepoint_directories = [x["Name"] for x in response["value"]]  # type: ignore

        # Verify that all local directories exist in SharePoint
        for local_dir in local_directories:
            if local_dir not in sharepoint_directories:
                error_message = f"Folder '{local_dir}' does not exist in SharePoint destination path '{self.sharepoint_destination_path}'."
                self.log_history.append(error_message)
                self.logger.error("[local_backup_lib] %s", error_message)
                raise BackupSourcePathError(
                    reason=f"Folder '{local_dir}' does not exist in SharePoint destination path '{self.sharepoint_destination_path}'."
                )

        # Check if the current folder only have files and each folder exist in Microsoft Sharepoint.
        if self.total_files == 0:
            no_files_message = (
                f"[local_backup_lib] {self.local_backup_source_path} has no files ⚠️"
            )
            self.log_history.append(no_files_message)
            self.logger.debug(no_files_message)
            raise BackupEmptyError

    async def _group_files_by_folder(self) -> dict[str, list[str]]:
        """Groups files by their parent folder."""
        backup_folder_exists = await self.dir_client.path_exists(
            self.local_backup_source_path
        )

        if not backup_folder_exists:
            return {}
        folder_names = await self.dir_client.listdir(self.local_backup_source_path)
        grouped = {}
        for folder_name in folder_names:
            is_folder = await self.dir_client.isdir(
                self.dir_client.join_paths(self.local_backup_source_path, folder_name)
            )
            if not is_folder:
                continue
            grouped[folder_name] = await self.dir_client.listdir(
                self.dir_client.join_paths(self.local_backup_source_path, folder_name)
            )
        return grouped

    async def _save_log_history(self) -> None:
        await self.files_client.write(
            WriteArgs(
                file_name="BACKUP_LOG_HISTORY.log",
                file_content="\n".join(self.log_history),
                mode="w",
            )
        )

    async def _generate_tasks(self) -> list:
        tasks = []
        for folder_name in self.grouped_files_by_folder:  # type: ignore
            count_files_in_dir = await count_files_in_directory(
                self.local_backup_source_path, folder_name
            )
            if count_files_in_dir == 0:
                empty_folder_message = (
                    f"[local_backup_lib] The folder '{folder_name}' is empty ⚠️"
                )
                self.logger.debug(empty_folder_message)
                self.log_history.append(empty_folder_message)
                continue
            extracting_files_message = (
                "[local_backup_lib]"
                + f" Extracting files from '{folder_name} ".center(15, "*")
            )
            self.log_history.append(extracting_files_message)
            self.logger.debug(extracting_files_message)
            for file_name in self.grouped_files_by_folder[folder_name]:  # type: ignore
                tasks.append(self._upload_and_log_progress_task(folder_name, file_name))

        return tasks

    async def export_file_to_sharepoint(
        self, folder_name: str, file_name: str, file_content: bytes
    ) -> tuple[bool, str]:
        """Uploads a file to the specified folder in SharePoint."""
        uploaded = None
        error_message = ""

        try:
            sharepoint_client = SharepointClient(
                SharepointClientInitArgs(
                    self.sharepoint_config, client_name="sharepoint_rest_api"
                )
            )
        except ConnectionError as error:
            raise SharepointClientError(error)

        async with sharepoint_client:
            try:
                folder_url = f"{self.sharepoint_destination_path}/{folder_name}"
                args = SpUploadFileArgs(
                    folder_relative_url=folder_url,
                    file_content=file_content,
                    file_name=file_name,
                )
                await sharepoint_client.upload_file(args)
                uploaded = True
            except ConnectionError as error:
                error_message = str(error)
                uploaded = False

        return uploaded, error_message

    async def _upload_and_log_progress_task(self, folder_name, file_name) -> dict:
        """Task for uploads a file and logs progress."""
        uploading_message = (
            f"[local_backup_lib] Uploading file '{file_name}' from '{folder_name}' "
        )
        self.log_history.append(uploading_message)
        self.logger.debug(uploading_message)
        file_path = self.dir_client.join_paths(
            self.local_backup_source_path, folder_name, file_name
        )
        file_content = await self.files_client.read(ReadArgs(file_path, mode="rb"))
        uploaded, error_message = await self.export_file_to_sharepoint(
            folder_name,
            file_name,
            file_content,  # type: ignore
        )
        result_message = show_upload_result(uploaded, file_name)
        self.logger.debug(result_message)
        self.log_history.append(result_message)
        return {
            "parent_folder": folder_name,
            "file_name": file_name,
            "uploaded": uploaded,
            "error_message": error_message,
        }

    async def retry_upload_failed_files(self, results) -> None:
        failed_files = [item for item in results if not item["uploaded"]]
        tasks = []
        retry_message = f"[local_backup_lib] Retrying upload for {len(failed_files)} failed files... 🚨"
        self.log_history.append(retry_message)
        self.logger.debug(retry_message)
        for file in failed_files:
            tasks.append(
                self._upload_and_log_progress_task(
                    file["parent_folder"], file["file_name"]
                )
            )
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = calculate_percentage_uploaded(results, self.total_files)  # type: ignore
        if success < 100.0:
            raise BackupUploadError(
                reason=extract_error_message(self.logger, results, success)  # type: ignore
            )
        else:
            successful_upload_retry = (
                "[local_backup_lib] All files uploaded successfully after retry."
            )
            self.log_history.append(successful_upload_retry)
            self.logger.debug(successful_upload_retry)
            await self._save_log_history()
            return parse_execute_response(results)  # type: ignore

    async def execute(self):
        """Exports all files from the local backup folder to SharePoint cloud."""
        start_time = time()
        self.grouped_files_by_folder = await self._group_files_by_folder()
        self.total_files = sum(
            len(files) for files in self.grouped_files_by_folder.values()
        )

        # Check if the current folder only have files and each folder exist in Microsoft Sharepoint.
        await self._validate_backup_structure()

        # Create task for each file stored in the the local backup folder.
        tasks = await self._generate_tasks()

        # Execution of multiple asynchronous tasks for files migration.
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = calculate_percentage_uploaded(results, self.total_files)  # type: ignore

        if success < 100.0:
            await self.retry_upload_failed_files(results)
        else:
            end_time = time()
            backup_time = end_time - start_time
            successful_backup_message = (
                f"[local_backup_lib] Migration time: {backup_time:.2f} seconds ✨"
            )
            self.log_history.append(successful_backup_message)

            finished_backup_message = (
                "[local_backup_lib] All the files were uploaded successfully 🎉"
            )
            self.log_history.append(finished_backup_message)

            await self._save_log_history()
            return parse_execute_response(results)  # type: ignore
