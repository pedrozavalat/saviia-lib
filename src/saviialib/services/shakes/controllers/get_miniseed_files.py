from .types.get_miniseed_files_types import (
    GetMiniseedFilesControllerInput,
    GetMiniseedFilesControllerOutput,
)
from saviialib.services.shakes.use_cases.get_miniseed_files import (
    GetMiniseedFilesUseCase,
    GetMiniseedFilesUseCaseInput,
)
from http import HTTPStatus
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ShakesNoContentError,
)
from saviialib.general_types.error_types.common.common_types import SftpClientError


class GetMiniseedFilesController:
    def __init__(self, input: GetMiniseedFilesControllerInput) -> None:
        self.use_case = GetMiniseedFilesUseCase(
            GetMiniseedFilesUseCaseInput(
                raspberry_shakes=input.raspberry_shakes,
                username=input.config.sftp_user,
                password=input.config.sftp_password,
                ssh_key_path=input.config.ssh_key_path,
                port=input.config.sftp_port,
                logger=input.config.logger,
            )
        )

    async def execute(self) -> GetMiniseedFilesControllerOutput:
        try:
            res = await self.use_case.execute()
            return GetMiniseedFilesControllerOutput(
                message="The MiniSEED files have been downloaded succesfully!",
                status=HTTPStatus.OK.value,
                metadata=res.download_status,
            )
        except ShakesNoContentError as error:
            return GetMiniseedFilesControllerOutput(
                message="No files to upload.",
                status=HTTPStatus.NO_CONTENT.value,
                metadata={"error": error.__str__()},
            )
        except SftpClientError as error:
            return GetMiniseedFilesControllerOutput(
                message="An unexpected error ocurred during SFTP Client connection.",
                status=HTTPStatus.REQUEST_TIMEOUT.value,
                metadata={"error": error.__str__()},
            )
