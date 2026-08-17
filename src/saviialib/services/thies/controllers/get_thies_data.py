from http import HTTPStatus

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ThiesFetchingError,
    ValidationError,
)
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
)
from saviialib.general_types.error_types.common.common_types import (
    FtpClientError,
    CloudClientError,
)
from saviialib.services.thies.controllers.types.get_thies_data_types import (
    GetThiesDataControllerInput,
    GetThiesDataControllerOutput,
)
from .types.get_thies_data_schema import GET_THIES_DATA_SCHEMA
from saviialib.libs.cloud_client import (
    CloudClient,
    CloudClientInitArgs,
)
from saviialib.libs.ftp_client import (
    FTPClient,
    FtpClientInitArgs,
)
from saviialib.libs.files_client import (
    FilesClient,
    FilesClientInitArgs,
)
from saviialib.general_types.api.saviia_api_types import (
    FtpClientConfig,
    DatabricksConfig,
)
from saviialib.services.thies.use_cases.get_thies_data import (
    GetThiesDataUseCase,
)
from saviialib.services.thies.use_cases.types.get_thies_data_types import (
    GetThiesDataUseCaseInput,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.schema_validator_client import SchemaValidatorClient


class GetThiesDataController:
    def __init__(self, input: GetThiesDataControllerInput):
        self.input = input
        self.cloud_client = CloudClient(
            CloudClientInitArgs(
                DatabricksConfig(
                    databricks_host_url=input.config.databricks_host_url,
                    databricks_api_key=input.config.databricks_api_key,
                ),
                client_name=input.config.cloud_client_name,
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
        self.use_case = GetThiesDataUseCase(
            GetThiesDataUseCaseInput(
                ftp_client=self.thies_ftp_client,
                cloud_client=self.cloud_client,
                local_backup_path=input.config.local_backup_path,
                cloud_provider_destination_path=input.cloud_provider_destination_path,
                files_client=self.files_client,
                directory_client=self.dir_client,
                logger=input.config.logger,
            )
        )

    async def execute(self) -> GetThiesDataControllerOutput:
        try:
            SchemaValidatorClient(schema=GET_THIES_DATA_SCHEMA).validate(
                {
                    "cloud_provider_destination_path": self.input.cloud_provider_destination_path,
                    "local_backup_path": self.input.config.local_backup_path,
                    "ftp_host": self.input.ftp_host,
                    "ftp_port": self.input.ftp_port,
                    "ftp_user": self.input.ftp_user,
                    "ftp_password": self.input.ftp_password,
                }
            )
            output = await self.use_case.execute()
            if output.need_to_backup and not output.need_to_sync:
                msg = "Backup needed but no new data to sync to cloud provider."
            elif not output.need_to_backup and output.need_to_sync:
                msg = "New data should be synced to cloud provider."
            elif output.need_to_sync and output.need_to_backup:
                msg = "New data synced to cloud provider and backup needed."
            else:
                msg = "No new data to sync to cloud provider."
            return GetThiesDataControllerOutput(
                message=msg,
                status=HTTPStatus.OK.value,
                metadata={"data": output.__dict__},  # type: ignore
            )

        except ValidationError as error:
            return GetThiesDataControllerOutput(
                message="Invalid input data for getting THIES data.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except BackupSourcePathError as error:
            return GetThiesDataControllerOutput(
                message="The specified local backup source path does not exist.",
                status=HTTPStatus.NOT_FOUND.value,
                metadata={"error": error.__str__()},
            )

        except (AttributeError, NameError, ValueError) as error:
            return GetThiesDataControllerOutput(
                message="An unexpected error occurred during use case initialization.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except (FtpClientError, CloudClientError) as error:
            return GetThiesDataControllerOutput(
                message="An error occurred while initializing FTP or cloud provider client.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )

        except ThiesFetchingError as error:
            return GetThiesDataControllerOutput(
                message="An error occurred while fetching THIES data.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
