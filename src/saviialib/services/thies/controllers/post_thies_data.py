from http import HTTPStatus

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ValidationError,
)
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
    CloudClientDirectoryError,
    CloudClientFetchingError,
    CloudClientUploadError,
    ThiesConnectionError,
    ThiesFetchingError,
)
from saviialib.general_types.error_types.common.common_types import (
    EmptyDataError,
    FtpClientError,
    CloudClientError,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.files_client import FilesClient, FilesClientInitArgs
from saviialib.libs.ftp_client import FTPClient, FtpClientInitArgs
from saviialib.libs.cloud_client import (
    CloudClient,
    CloudClientInitArgs,
)
from saviialib.general_types.api.saviia_api_types import (
    FtpClientConfig,
    DatabricksConfig,
)
from saviialib.services.thies.controllers.types.post_thies_data_types import (
    PostThiesDataControllerInput,
    PostThiesDataControllerOutput,
)
from .types.post_thies_data_schema import POST_THIES_DATA_SCHEMA
from saviialib.services.thies.use_cases.post_thies_data import (
    PostThiesDataUseCase,
)
from saviialib.services.thies.use_cases.types.post_thies_data_types import (
    PostThiesDataUseCaseInput,
)
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.libs.log_client import (
    LogClient,
    LogClientArgs,
    LogStatus,
    DebugArgs,
    ErrorArgs,
    WarningArgs,
)


class PostThiesDataController:
    def __init__(self, input: PostThiesDataControllerInput):
        self.input = input
        self.logger = LogClient(
            LogClientArgs(
                "logging",
                service_name="thies",
                class_name="post_thies_data_controller",
                logger=input.config.logger,
            )
        )
        self.cloud_client = CloudClient(
            CloudClientInitArgs(
                DatabricksConfig(
                    databricks_api_key=self.input.config.databricks_api_key,
                    databricks_host_url=self.input.config.databricks_host_url,
                ),
                client_name=self.input.config.cloud_client_name,
            )
        )
        self.files_client = FilesClient(
            FilesClientInitArgs(client_name="aiofiles_client")
        )
        self.thies_ftp_client = FTPClient(
            FtpClientInitArgs(
                FtpClientConfig(
                    ftp_host=input.ftp_host,
                    ftp_password=input.ftp_password,
                    ftp_port=input.ftp_port,
                    ftp_user=input.ftp_user,
                ),
                client_name="ftplib_client",
            )
        )
        self.dir_client = DirectoryClient(DirectoryClientArgs(client_name="os_client"))
        self.use_case = PostThiesDataUseCase(
            PostThiesDataUseCaseInput(
                ftp_client=self.thies_ftp_client,
                cloud_client=self.cloud_client,
                files_client=self.files_client,
                directory_client=self.dir_client,
                cloud_provider_destination_path=input.cloud_provider_destination_path,
                ftp_server_folders_path=input.ftp_server_folders_path,
                local_backup_source_path=input.local_backup_source_path,
                need_to_sync=input.need_to_sync,
                need_to_backup=input.need_to_backup,
                logger=input.config.logger,
            )
        )

    async def execute(self) -> PostThiesDataControllerOutput:
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(status=LogStatus.STARTED))
        try:
            SchemaValidatorClient(schema=POST_THIES_DATA_SCHEMA).validate(
                {
                    "local_backup_path": self.input.config.local_backup_path,
                    "ftp_host": self.input.ftp_host,
                    "ftp_port": self.input.ftp_port,
                    "ftp_user": self.input.ftp_user,
                    "ftp_password": self.input.ftp_password,
                    "need_to_sync": self.input.need_to_sync,
                    "need_to_backup": self.input.need_to_backup,
                    "cloud_provider_destination_path": self.input.cloud_provider_destination_path,
                    "ftp_server_folders_path": self.input.ftp_server_folders_path,
                    "local_backup_source_path": self.input.local_backup_source_path,
                }
            )
            data = await self.use_case.execute()
            if self.use_case.need_to_backup and self.use_case.need_to_sync:
                msg = "THIES data was backed up and synced successfully"
            elif self.use_case.need_to_backup:
                msg = "THIES backup was processed successfully"
            elif self.use_case.need_to_sync:
                msg = "THIES data was synced successfully"
            else:
                msg = "No operation was requested"
            self.logger.debug(
                DebugArgs(
                    status=LogStatus.SUCCESSFUL,
                    metadata={"msg": msg},
                )
            )
            return PostThiesDataControllerOutput(
                message=msg,
                status=HTTPStatus.OK.value,
                metadata={"data": data},  # type: ignore
            )
        except ValidationError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            return PostThiesDataControllerOutput(
                message="Invalid input data for posting THIES data.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except EmptyDataError:
            self.logger.warning(
                WarningArgs(
                    status=LogStatus.FAILED,
                    metadata={"msg": "No files to upload"},
                )
            )
            return PostThiesDataControllerOutput(
                message="No files to upload", status=HTTPStatus.NO_CONTENT.value
            )
        except (AttributeError, NameError, ValueError) as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            return PostThiesDataControllerOutput(
                message="An unexpected error occurred during use case initialization.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except FtpClientError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            return PostThiesDataControllerOutput(
                message="Ftp Client initialization fails.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except CloudClientError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            return PostThiesDataControllerOutput(
                message="Sharepoint Client initialization fails.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        except CloudClientFetchingError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            return PostThiesDataControllerOutput(
                message="An error occurred while retrieving file names from SAVIIA Cloud provider",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except CloudClientUploadError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            return PostThiesDataControllerOutput(
                message="An error ocurred while uploading files to RCER Cloud",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except CloudClientDirectoryError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            return PostThiesDataControllerOutput(
                message="An error ocurred while extracting folders from SAVIIA Cloud provider",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except ThiesFetchingError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            return PostThiesDataControllerOutput(
                message="An error ocurred while retrieving file names from THIES FTP Server.",
                status=HTTPStatus.NO_CONTENT.value,
                metadata={"error": error.__str__()},
            )
        except ThiesConnectionError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            return PostThiesDataControllerOutput(
                message="Unable to connect to THIES Data Logger FTP Server.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        except BackupSourcePathError as error:
            self.logger.error(
                ErrorArgs(status=LogStatus.ERROR, metadata={"msg": error.__str__()})
            )
            return PostThiesDataControllerOutput(
                message="The specified local backup source path does not exist.",
                status=HTTPStatus.NOT_FOUND.value,
                metadata={"error": error.__str__()},
            )
