from http import HTTPStatus

from rcer_iot_client_pkg.general_types.error_types.api.update_thies_data_error_types import (
    FetchCloudFileNamesError,
    ThiesUploadEmptyError,
)
from rcer_iot_client_pkg.general_types.error_types.common.common_types import (
    FtpClientError,
    HttpClientError,
)
from rcer_iot_client_pkg.services.epii.controllers.types.update_thies_data_types import (
    UpdateThiesDataControllerInput,
    UpdateThiesDataControllerOutput,
)
from rcer_iot_client_pkg.services.epii.use_cases.types import (
    UpdateThiesDataUseCaseInput,
)
from rcer_iot_client_pkg.services.epii.use_cases.update_thies_data import (
    UpdateThiesDataUseCase,
)


class UpdateThiesDataController:
    def __init__(self, input: UpdateThiesDataControllerInput):
        self.use_case = UpdateThiesDataUseCase(
            UpdateThiesDataUseCaseInput(**input.__dict__)
        )

    async def execute(self) -> UpdateThiesDataControllerOutput:
        try:
            data = await self.use_case.execute()
            return UpdateThiesDataControllerOutput(
                message="THIES was synced successfully",
                status=HTTPStatus.OK.value,
                metadata={"data": data},
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

        except HttpClientError as error:
            return UpdateThiesDataControllerOutput(
                message="Http Client initialization fails.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )

        except FetchCloudFileNamesError as error:
            return UpdateThiesDataControllerOutput(
                message="An error occurred while retrieving file names from the RCER cloud",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        except ThiesUploadEmptyError as error:
            return UpdateThiesDataControllerOutput(
                message="No files were found to upload.",
                status=HTTPStatus.NO_CONTENT.value,
                metadata={"error": error.__str__()},
            )
