from http import HTTPStatus

from saviialib.general_types.error_types.api.epii_api_error_types import (
    SharePointFetchingError,
    ThiesConnectionError,
    ThiesFetchingError,
    SharePointUploadError,
)
from saviialib.general_types.error_types.common.common_types import (
    EmptyDataError,
    FtpClientError,
    SharepointClientError,
)
from saviialib.services.epii.controllers.types.update_thies_data_types import (
    UpdateThiesDataControllerInput,
    UpdateThiesDataControllerOutput,
)
from saviialib.services.epii.use_cases.types import (
    UpdateThiesDataUseCaseInput,
    SharepointConfig,
    FtpClientConfig,
)
from saviialib.services.epii.use_cases.update_thies_data import (
    UpdateThiesDataUseCase,
)


class UpdateThiesDataController:
    def __init__(self, input: UpdateThiesDataControllerInput):
        self.use_case = UpdateThiesDataUseCase(
            UpdateThiesDataUseCaseInput(
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
            )
        )

    async def execute(self) -> UpdateThiesDataControllerOutput:
        try:
            data = await self.use_case.execute()
            return UpdateThiesDataControllerOutput(
                message="THIES was synced successfully",
                status=HTTPStatus.OK.value,
                metadata={"data": data},
            )
        except EmptyDataError:
            return UpdateThiesDataControllerOutput(
                message="No files to upload", status=HTTPStatus.NO_CONTENT.value
            )

        except (AttributeError, NameError, ValueError) as error:
            return UpdateThiesDataControllerOutput(
                message="An unexpected error occurred during use case initialization.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except FtpClientError as error:
            return UpdateThiesDataControllerOutput(
                message="Ftp Client initialization fails.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )

        except SharepointClientError as error:
            return UpdateThiesDataControllerOutput(
                message="Sharepoint Client initialization fails.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )

        except SharePointFetchingError as error:
            return UpdateThiesDataControllerOutput(
                message="An error occurred while retrieving file names from Microsoft SharePoint",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )

        except SharePointUploadError as error:
            return UpdateThiesDataControllerOutput(
                message="An error oucrred while uploading files to RCER Cloud",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )

        except ThiesFetchingError as error:
            return UpdateThiesDataControllerOutput(
                message="An error ocurred while retrieving file names from THIES FTP Server.",
                status=HTTPStatus.NO_CONTENT.value,
                metadata={"error": error.__str__()},
            )

        except ThiesConnectionError as error:
            return UpdateThiesDataControllerOutput(
                message="Unable to connect to THIES Data Logger FTP Server.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
