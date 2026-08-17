from http import HTTPStatus

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
    ValidationError,
)
from saviialib.general_types.error_types.common.common_types import (
    EmptyDataError,
    CloudClientError,
)
from saviialib.libs.cloud_client import CloudClient, CloudClientInitArgs
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.files_client import FilesClient, FilesClientInitArgs
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
        self.cloud_client = CloudClient(
            CloudClientInitArgs(
                config=input.config,
                client_name=input.config.client_name,
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
                cloud_client=self.cloud_client,
                files_client=self.files_client,
                directory_client=self.directory_client,
                local_backup_path=input.config.local_backup_path,
                local_folder_path=input.local_folder_path,
                cloud_provider_destination_path=input.cloud_provider_destination_path,
                logger=input.config.logger,
            )
        )

    async def execute(self) -> ExportFilesControllerOutput:
        try:
            data = {
                "local_backup_path": self.input.config.local_backup_path,
                "local_folder_path": self.input.local_folder_path,
                "cloud_provider_destination_path": self.input.cloud_provider_destination_path,
            }

            SchemaValidatorClient(schema=EXPORT_FILES_SCHEMA).validate(data)

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
        except (BackupSourcePathError, OSError) as error:
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
        except CloudClientError as error:
            return ExportFilesControllerOutput(
                message="Cloud Client provider initialization fails.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        # except ConnectionError as error:
        #     return ExportFilesControllerOutput(
        #         message="An unexpected error occurred during SharePoint synchronization.",
        #         status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
        #         metadata={"error": error.__str__()},
        #     )
