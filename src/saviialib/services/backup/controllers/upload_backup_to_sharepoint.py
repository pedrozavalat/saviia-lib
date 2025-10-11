from http import HTTPStatus
from saviialib.general_types.api.saviia_api_types import SharepointConfig

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupUploadError,
    BackupSourcePathError,
    BackupEmptyError,
)
from saviialib.general_types.error_types.common.common_types import (
    EmptyDataError,
    SharepointClientError,
)
from saviialib.services.backup.controllers.types.upload_backup_to_sharepoint_types import (
    UploadBackupToSharepointControllerInput,
    UploadBackupToSharepointControllerOutput,
)
from saviialib.services.backup.use_cases.types.upload_backup_to_sharepoint_types import (
    UploadBackupToSharepointUseCaseInput,
)
from saviialib.services.backup.use_cases.upload_backup_to_sharepoint import (
    UploadBackupToSharepointUsecase,
)


class UploadBackupToSharepointController:
    def __init__(self, input: UploadBackupToSharepointControllerInput):
        self.use_case = UploadBackupToSharepointUsecase(
            UploadBackupToSharepointUseCaseInput(
                sharepoint_config=SharepointConfig(
                    sharepoint_client_id=input.config.sharepoint_client_id,
                    sharepoint_client_secret=input.config.sharepoint_client_secret,
                    sharepoint_site_name=input.config.sharepoint_site_name,
                    sharepoint_tenant_name=input.config.sharepoint_tenant_name,
                    sharepoint_tenant_id=input.config.sharepoint_tenant_id,
                ),
                local_backup_source_path=input.local_backup_source_path,
                sharepoint_destination_path=input.sharepoint_destination_path,
                logger=input.config.logger,
            )
        )

    async def execute(self) -> UploadBackupToSharepointControllerOutput:
        try:
            data = await self.use_case.execute()
            return UploadBackupToSharepointControllerOutput(
                message="Local backup was migrated successfully",
                status=HTTPStatus.OK.value,
                metadata={"data": data},  # type: ignore
            )
        except EmptyDataError:
            return UploadBackupToSharepointControllerOutput(
                message="No files to upload", status=HTTPStatus.NO_CONTENT.value
            )

        except (AttributeError, NameError, ValueError) as error:
            return UploadBackupToSharepointControllerOutput(
                message="An unexpected error occurred during use case initialization.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )

        except SharepointClientError as error:
            return UploadBackupToSharepointControllerOutput(
                message="Sharepoint Client initialization fails.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )

        except BackupUploadError as error:
            return UploadBackupToSharepointControllerOutput(
                message="An error occurred during local backup",
                status=HTTPStatus.MULTI_STATUS.value,
                metadata={"error": error.__str__()},
            )

        except BackupSourcePathError as error:
            return UploadBackupToSharepointControllerOutput(
                message="Invalid local backup source path provided.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except BackupEmptyError as error:
            return UploadBackupToSharepointControllerOutput(
                message="Each folder in the backup folder is empty. Check out again",
                status=HTTPStatus.EXPECTATION_FAILED.value,
                metadata={"error": error.__str__()},
            )
