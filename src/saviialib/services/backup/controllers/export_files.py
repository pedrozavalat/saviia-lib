from http import HTTPStatus

from saviialib.general_types.api.saviia_api_types import SharepointConfig
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
    ValidationError,
)
from saviialib.general_types.error_types.common.common_types import (
    EmptyDataError,
    SharepointClientError,
)
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.files_client import FilesClient, FilesClientInitArgs
from saviialib.libs.sharepoint_client import SharepointClient, SharepointClientInitArgs
from saviialib.services.backup.controllers.types.export_files_schema import (
    EXPORT_FILES_SCHEMA,
)
from saviialib.services.backup.controllers.types.export_files_types import (
    ExportFilesControllerInput,
    ExportFilesControllerOutput,
)
from saviialib.services.backup.use_cases.export_files import ExportFilesUseCase
from saviialib.services.backup.use_cases.types.export_files_types import (
    ExportFilesUseCaseInput,
)


class ExportFilesController:
    def __init__(self, input: ExportFilesControllerInput):
        self.input = input
        self.sharepoint_client = SharepointClient(
            SharepointClientInitArgs(
                SharepointConfig(
                    sharepoint_client_id=input.config.sharepoint_client_id,
                    sharepoint_client_secret=input.config.sharepoint_client_secret,
                    sharepoint_site_name=input.config.sharepoint_site_name,
                    sharepoint_tenant_name=input.config.sharepoint_tenant_name,
                    sharepoint_tenant_id=input.config.sharepoint_tenant_id,
                ),
                client_name="sharepoint_rest_api",
            )
        )
        self.files_client = FilesClient(
            FilesClientInitArgs(client_name="aiofiles_client")
        )
        self.directory_client = DirectoryClient(
            DirectoryClientArgs(client_name="os_client")
        )
        self.use_case = ExportFilesUseCase(
            ExportFilesUseCaseInput(
                sharepoint_client=self.sharepoint_client,
                files_client=self.files_client,
                directory_client=self.directory_client,
                local_backup_path=input.config.local_backup_path,
                local_folder_path=input.local_folder_path,
                sharepoint_destination_path=input.sharepoint_destination_path,
                logger=input.config.logger,
            )
        )

    async def execute(self) -> ExportFilesControllerOutput:
        try:
            SchemaValidatorClient(schema=EXPORT_FILES_SCHEMA).validate(
                {
                    "sharepoint_client_id": self.input.config.sharepoint_client_id,
                    "sharepoint_client_secret": self.input.config.sharepoint_client_secret,
                    "sharepoint_tenant_id": self.input.config.sharepoint_tenant_id,
                    "sharepoint_tenant_name": self.input.config.sharepoint_tenant_name,
                    "sharepoint_site_name": self.input.config.sharepoint_site_name,
                    "local_backup_path": self.input.config.local_backup_path,
                    "local_folder_path": self.input.local_folder_path,
                    "sharepoint_destination_path": self.input.sharepoint_destination_path,
                }
            )
            output = await self.use_case.execute()
            data = output.__dict__
            total_synced_files = output.__dict__.get("total_synced_files", 0)

            if total_synced_files == 0:
                return ExportFilesControllerOutput(
                    message="No files were exported.",
                    status=HTTPStatus.OK.value,
                    metadata={"data": data},
                )
            return ExportFilesControllerOutput(
                message="Folder files exported successfully.",
                status=HTTPStatus.OK.value,
                metadata={"data": output.__dict__},
            )
        except EmptyDataError:
            return ExportFilesControllerOutput(
                message="No files to export.",
                status=HTTPStatus.NO_CONTENT.value,
            )
        except BackupSourcePathError as error:
            return ExportFilesControllerOutput(
                message="Invalid local backup path or folder.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except (ValidationError, ValueError) as error:
            return ExportFilesControllerOutput(
                message="Invalid input data for exporting files.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except SharepointClientError as error:
            return ExportFilesControllerOutput(
                message="Sharepoint Client initialization fails.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        except ConnectionError as error:
            return ExportFilesControllerOutput(
                message="An unexpected error occurred during SharePoint synchronization.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
