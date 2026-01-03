from http import HTTPStatus

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
from saviialib.services.backup.use_cases.types import (
    GetThiesDataUseCaseInput,
    SharepointConfig,
    FtpClientConfig,
)
from saviialib.services.thies.use_cases.get_thies_data import (
    GetThiesDataUseCase,
)


class GetThiesDataController:
    def __init__(self, input: GetThiesDataControllerInput):
        self.use_case = GetThiesDataUseCase(
            GetThiesDataUseCaseInput(
                ftp_config=FtpClientConfig(
                    ftp_host=input.config.ftp_host,
                    ftp_password=input.config.ftp_password,
                    ftp_port=input.config.ftp_port,
                    ftp_user=input.config.ftp_user,
                ),
                sharepoint_config=SharepointConfig(
                    sharepoint_client_id=input.config.sharepoint_client_id,
                    sharepoint_client_secret=input.config.sharepoint_client_secret,
                    sharepoint_site_name=input.config.sharepoint_site_name,
                    sharepoint_tenant_name=input.config.sharepoint_tenant_name,
                    sharepoint_tenant_id=input.config.sharepoint_tenant_id,
                ),
                local_backup_path=input.local_backup_path
                
            )
        )

    async def execute(self) -> GetThiesDataControllerOutput:
        try:
            output = await self.use_case.execute()
            if output.need_to_backup and not output.need_to_sync:
                msg = 'Backup needed but no new data to sync to Microsoft SharePoint.'
            elif not output.need_to_backup and output.need_to_sync:
                msg = 'New data should be synced to Microsoft SharePoint.'
            elif output.need_to_sync and output.need_to_backup:
                msg = 'New data synced to SharePoint and backup needed.'
            else: 
                msg = 'No new data to sync to Microsoft SharePoint.'
            return GetThiesDataControllerOutput(
                message=msg,
                status=HTTPStatus.OK.value,
                metadata={"data": output.__dict__},  # type: ignore
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
        