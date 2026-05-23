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
    SharepointClientError,
)
from saviialib.services.thies.controllers.types.get_thies_data_types import (
    GetThiesDataControllerInput,
    GetThiesDataControllerOutput,
)
from .types.get_thies_data_schema import GET_THIES_DATA_SCHEMA
from saviialib.libs.sharepoint_client import (
    SharepointClient,
    SharepointClientInitArgs,
)
from saviialib.libs.ftp_client import (
    FTPClient,
    FtpClientInitArgs,
)
from saviialib.libs.files_client import (
    FilesClient,
    FilesClientInitArgs,
)
from saviialib.services.backup.use_cases.types import (
    SharepointConfig,
    FtpClientConfig,
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
                sharepoint_client=self.sharepoint_client,
                local_backup_path=input.config.local_backup_path,
                sharepoint_destination_path=input.sharepoint_destination_path,
                files_client=self.files_client,
                directory_client=self.dir_client,
            )
        )

    async def execute(self) -> GetThiesDataControllerOutput:
        try:
            SchemaValidatorClient(schema=GET_THIES_DATA_SCHEMA).validate(
                {
                    "sharepoint_client_id": self.input.config.sharepoint_client_id,
                    "sharepoint_client_secret": self.input.config.sharepoint_client_secret,
                    "sharepoint_tenant_id": self.input.config.sharepoint_tenant_id,
                    "sharepoint_tenant_name": self.input.config.sharepoint_tenant_name,
                    "sharepoint_site_name": self.input.config.sharepoint_site_name,
                    "local_backup_path": self.input.config.local_backup_path,
                    "sharepoint_destination_path": self.input.sharepoint_destination_path,
                    "ftp_host": self.input.ftp_host,
                    "ftp_port": self.input.ftp_port,
                    "ftp_user": self.input.ftp_user,
                    "ftp_password": self.input.ftp_password,
                }
            )
            output = await self.use_case.execute()
            if output.need_to_backup and not output.need_to_sync:
                msg = "Backup needed but no new data to sync to Microsoft SharePoint."
            elif not output.need_to_backup and output.need_to_sync:
                msg = "New data should be synced to Microsoft SharePoint."
            elif output.need_to_sync and output.need_to_backup:
                msg = "New data synced to SharePoint and backup needed."
            else:
                msg = "No new data to sync to Microsoft SharePoint."
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
        except (FtpClientError, SharepointClientError) as error:
            return GetThiesDataControllerOutput(
                message="An error occurred while initializing FTP or SharePoint client.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
            
        except ThiesFetchingError as error:
            return GetThiesDataControllerOutput(
                message="An error occurred while fetching THIES data.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
