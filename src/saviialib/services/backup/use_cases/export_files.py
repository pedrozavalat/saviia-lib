from logging import Logger

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
)
from saviialib.general_types.error_types.common.common_types import (
    EmptyDataError,
)
from saviialib.libs.cloud_client import (
    CloudClientCreateFolderArgs,
    CloudClientListFilesArgs,
    CloudClientUploadFileArgs,
    CloudClientResolveUrlArgs,
)
from saviialib.libs.files_client import ReadArgs
from saviialib.libs.log_client import (
    DebugArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
    ErrorArgs,
)

from .types.export_files_types import ExportFilesUseCaseInput, ExportFilesUseCaseOutput


class ExportFilesUseCase:
    def __init__(self, input: ExportFilesUseCaseInput):
        self.cloud_client = input.cloud_client
        self.files_client = input.files_client
        self.dir_client = input.directory_client
        self.local_backup_path = input.local_backup_path
        self.local_folder_path = input.local_folder_path.strip("/")
        self.cloud_provider_destination_path = (
            input.cloud_provider_destination_path.rstrip("/")
        )
        self.cloud_client_name = getattr(input.cloud_client, "client_name", None)
        self.sharepoint_site_name = getattr(input.cloud_client, "site_name", None)
        self.sharepoint_base_url = (
            f"/sites/{self.sharepoint_site_name}" if self.sharepoint_site_name else ""
        )
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

    def _resolve_cloud_provider_url(self, folder_path: str) -> str:
        return self.cloud_client.resolve_url(CloudClientResolveUrlArgs(folder_path))

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
            msg_error = f"'{folder_path}' doesn't exist."
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"error": msg_error}))
            raise BackupSourcePathError(reason=msg_error)
        if not await self.dir_client.isdir(folder_path):
            msg_error = f"'{folder_path}' is not a directory."
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"error": msg_error}))
            raise BackupSourcePathError(reason=msg_error)
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return folder_path

    async def _get_local_files(
        self, folder_path: str
    ) -> dict[str, dict[str, int | str]]:
        self.log_client.method_name = "_get_local_files"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        entries = await self.dir_client.listdir(folder_path, more_info=True)
        if len(entries) == 0:
            raise EmptyDataError(reason=f"No files found in '{folder_path}'.")

        files: dict[str, dict[str, int | str]] = {}
        for name, size in entries:
            full_path = self.dir_client.join_paths(folder_path, name)
            if await self.dir_client.isdir(full_path):
                raise ValueError("The source folder must contain files only.")
            files[name] = {"path": full_path, "size": int(size)}
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return files

    async def _get_cloud_files(self, destination_folder_path: str) -> dict[str, int]:
        self.log_client.method_name = "_get_cloud_files"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        relative_url = self._resolve_cloud_provider_url(destination_folder_path)
        async with self.cloud_client:
            response = await self.cloud_client.list_files(
                CloudClientListFilesArgs(folder_relative_url=relative_url)
            )
        if isinstance(response, dict):
            cloud_files = {
                item["Name"]: int(item["Length"])
                for item in response.get("value", [])  # type: ignore
            }
        else:
            cloud_files = {
                item["name"]: int(item.get("file_size", 0))
                for item in response
                if not item.get("is_directory", False)
            }
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return cloud_files

    def _get_pending_files(
        self,
        local_files: dict[str, dict[str, int | str]],
        cloud_files: dict[str, int],
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
        local_files: dict[str, dict[str, int | str]],
        destination_folder_path: str,
    ) -> list[str]:
        self.log_client.method_name = "_upload_pending_files"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        synced_files = []
        relative_url = self._resolve_cloud_provider_url(destination_folder_path)
        async with self.cloud_client:
            for file_name in pending_files:
                file_path = str(local_files[file_name]["path"])
                file_content = await self.files_client.read(
                    ReadArgs(file_path=file_path, mode="rb")
                )
                await self.cloud_client.upload_file(
                    CloudClientUploadFileArgs(
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
        # Local file validation
        folder_path = await self._validate_source_folder()
        local_files = await self._get_local_files(folder_path)
        # Reviewing of destination folder and relative url of the cloud provider
        destination_folder_path = "/".join(
            [
                self.cloud_provider_destination_path.rstrip("/"),
                folder_path.strip("/"),
            ]
        )

        relative_url = self._resolve_cloud_provider_url(destination_folder_path)

        async with self.cloud_client:
            await self.cloud_client.create_folder(
                CloudClientCreateFolderArgs(folder_relative_url=relative_url)
            )
        cloud_files = await self._get_cloud_files(destination_folder_path)
        pending_files = self._get_pending_files(local_files, cloud_files)
        synced_files = await self._upload_pending_files(
            pending_files,
            local_files,
            destination_folder_path,
        )

        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return ExportFilesUseCaseOutput(
            synced_files=synced_files,
            total_local_files=len(local_files),
            total_cloud_files=len(cloud_files),
            total_pending_files=len(pending_files),
            total_synced_files=len(synced_files),
        )
