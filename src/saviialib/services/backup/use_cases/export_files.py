from logging import Logger
from typing import Dict

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
)
from saviialib.general_types.error_types.common.common_types import (
    EmptyDataError,
)
from saviialib.libs.files_client import ReadArgs
from saviialib.libs.log_client import DebugArgs, LogClient, LogClientArgs, LogStatus
from saviialib.libs.sharepoint_client import (
    SpCreateFolderArgs,
    SpListFilesArgs,
    SpUploadFileArgs,
)

from .types.export_files_types import ExportFilesUseCaseInput, ExportFilesUseCaseOutput


class ExportFilesUseCase:
    def __init__(self, input: ExportFilesUseCaseInput):
        self.sharepoint_client = input.sharepoint_client
        self.files_client = input.files_client
        self.dir_client = input.directory_client
        self.local_backup_path = input.local_backup_path
        self.local_folder_path = input.local_folder_path.strip("/")
        self.sharepoint_destination_path = input.sharepoint_destination_path.rstrip("/")
        self.sharepoint_base_url = f"/sites/{self.sharepoint_client.site_name}"
        self.logger: Logger = input.logger
        self.log_client = LogClient(
            LogClientArgs(
                client_name="logging",
                class_name="export_files",
                service_name="backup",
                active_record=True,
                logger=input.logger,
            )
        )

    def _resolve_sharepoint_url(self, folder_path: str) -> str:
        """Resolve folder path to server-relative SharePoint URL when needed."""
        folder_path = folder_path.rstrip("/")
        if folder_path.startswith(self.sharepoint_base_url):
            return folder_path
        return f"{self.sharepoint_base_url}/{folder_path.lstrip('/')}"

    async def _validate_source_folder(self) -> str:
        self.log_client.method_name = "_validate_source_folder"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        if not await self.dir_client.path_exists(self.local_backup_path):
            raise BackupSourcePathError(
                reason=f"'{self.local_backup_path}' doesn't exist."
            )

        folder_path = self.dir_client.join_paths(
            self.local_backup_path, self.local_folder_path
        )
        if not await self.dir_client.path_exists(folder_path):
            raise BackupSourcePathError(reason=f"'{folder_path}' doesn't exist.")
        if not await self.dir_client.isdir(folder_path):
            raise BackupSourcePathError(reason=f"'{folder_path}' is not a directory.")
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return folder_path

    async def _get_local_files(
        self, folder_path: str
    ) -> Dict[str, Dict[str, int | str]]:
        self.log_client.method_name = "_get_local_files"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        entries = await self.dir_client.listdir(folder_path, more_info=True)
        if len(entries) == 0:
            raise EmptyDataError(reason=f"No files found in '{folder_path}'.")

        files: Dict[str, Dict[str, int | str]] = {}
        for name, size in entries:
            full_path = self.dir_client.join_paths(folder_path, name)
            if await self.dir_client.isdir(full_path):
                raise ValueError("The source folder must contain files only.")
            files[name] = {"path": full_path, "size": int(size)}
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return files

    async def _get_cloud_files(self, sharepoint_folder_path: str) -> Dict[str, int]:
        self.log_client.method_name = "_get_cloud_files"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        relative_url = self._resolve_sharepoint_url(sharepoint_folder_path)
        async with self.sharepoint_client:
            response = await self.sharepoint_client.list_files(
                SpListFilesArgs(folder_relative_url=relative_url)
            )
        cloud_files = {
            item["Name"]: int(item["Length"])
            for item in response.get("value", [])  # type: ignore
        }
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return cloud_files

    def _get_pending_files(
        self,
        local_files: Dict[str, Dict[str, int | str]],
        cloud_files: Dict[str, int],
    ) -> list[str]:
        pending_files = []
        for file_name, file_data in local_files.items():
            local_size = int(file_data["size"])
            cloud_size = cloud_files.get(file_name)
            if cloud_size is None:
                pending_files.append(file_name)
                continue
            # Keep parity with THIES sync rules: when one side reports 0,
            # treat size metadata as unknown and avoid forcing a full resync.
            if local_size > 0 and cloud_size > 0 and cloud_size != local_size:
                pending_files.append(file_name)
        return pending_files

    async def _upload_pending_files(
        self,
        pending_files: list[str],
        local_files: Dict[str, Dict[str, int | str]],
        sharepoint_folder_path: str,
    ) -> list[str]:
        self.log_client.method_name = "_upload_pending_files"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        synced_files = []
        relative_url = self._resolve_sharepoint_url(sharepoint_folder_path)
        async with self.sharepoint_client:
            for file_name in pending_files:
                file_path = str(local_files[file_name]["path"])
                file_content = await self.files_client.read(
                    ReadArgs(file_path=file_path, mode="rb")
                )
                await self.sharepoint_client.upload_file(
                    SpUploadFileArgs(
                        folder_relative_url=relative_url,
                        file_name=file_name,
                        file_content=file_content,  # type: ignore
                    )
                )
                synced_files.append(file_name)
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return synced_files

    async def execute(self) -> ExportFilesUseCaseOutput:
        self.log_client.method_name = "execute"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        folder_path = await self._validate_source_folder()
        local_files = await self._get_local_files(folder_path)

        sharepoint_folder_path = self.sharepoint_destination_path
        relative_url = self._resolve_sharepoint_url(sharepoint_folder_path)
        async with self.sharepoint_client:
            await self.sharepoint_client.create_folder(
                SpCreateFolderArgs(folder_relative_url=relative_url)
            )
        cloud_files = await self._get_cloud_files(sharepoint_folder_path)
        pending_files = self._get_pending_files(local_files, cloud_files)
        synced_files = await self._upload_pending_files(
            pending_files,
            local_files,
            sharepoint_folder_path,
        )

        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return ExportFilesUseCaseOutput(
            synced_files=synced_files,
            total_local_files=len(local_files),
            total_cloud_files=len(cloud_files),
            total_pending_files=len(pending_files),
            total_synced_files=len(synced_files),
        )
