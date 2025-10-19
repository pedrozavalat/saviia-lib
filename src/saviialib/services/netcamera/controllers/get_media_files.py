from .types.get_media_files_types import (
    GetMediaFilesControllerInput,
    GetMediaFilesControllerOutput,
)
from saviialib.services.netcamera.use_cases.get_media_files import (
    GetMediaFilesUseCase,
    GetMediaFilesUseCaseInput,
)
from http import HTTPStatus
from saviialib.general_types.error_types.api.saviia_netcamera_error_types import (
    NetcameraConnectionError,
)


class GetMediaFilesController:
    def __init__(self, input: GetMediaFilesControllerInput) -> None:
        self.use_case = GetMediaFilesUseCase(
            GetMediaFilesUseCaseInput(
                cameras=input.cameras,
                username=input.config.username,
                password=input.config.password,
                protocol=input.config.protocol,
                logger=input.config.logger,
                destination_path=input.config.destination_path,
            )
        )

    async def execute(self) -> GetMediaFilesControllerOutput:
        try:
            _ = await self.use_case.execute()
            return GetMediaFilesControllerOutput(
                message="The extraction of media files was successfully!",
                status=HTTPStatus.OK.value,
            )
        except NetcameraConnectionError as error:
            return GetMediaFilesControllerOutput(
                message="An unnexpected error ocurred while extractingphotos and videos.",
                status=HTTPStatus.GATEWAY_TIMEOUT.value,
                metadata={"error": error.__str__()},
            )
