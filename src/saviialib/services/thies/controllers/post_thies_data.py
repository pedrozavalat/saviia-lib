from http import HTTPStatus

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
    SharePointDirectoryError,
    SharePointFetchingError,
    SharePointUploadError,
    ThiesConnectionError,
    ThiesFetchingError,
)
from saviialib.general_types.error_types.common.common_types import (
    EmptyDataError,
    FtpClientError,
    SharepointClientError,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.files_client import FilesClient, FilesClientInitArgs
from saviialib.libs.ftp_client import FTPClient, FtpClientInitArgs
from saviialib.libs.sharepoint_client import (
    SharepointClient,
    SharepointClientInitArgs,
)
from saviialib.services.backup.use_cases.types import FtpClientConfig, SharepointConfig
from saviialib.services.thies.controllers.types.post_thies_data_types import (
    PostThiesDataControllerInput,
    PostThiesDataControllerOutput,
)
from saviialib.services.thies.use_cases.post_thies_data import (
    PostThiesDataUseCase,
)
from saviialib.services.thies.use_cases.types.post_thies_data_types import (
    PostThiesDataUseCaseInput,
)


class PostThiesDataController:
    def __init__(self, input: PostThiesDataControllerInput):
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
        self.use_case = PostThiesDataUseCase(
            PostThiesDataUseCaseInput(
                ftp_client=self.thies_ftp_client,
                sharepoint_client=self.sharepoint_client,
                files_client=self.files_client,
                directory_client=self.dir_client,
                sharepoint_destination_path=input.sharepoint_destination_path,
                ftp_server_folders_path=input.ftp_server_folders_path,
                local_backup_source_path=input.local_backup_source_path,
                need_to_sync=input.need_to_sync,
                need_to_backup=input.need_to_backup,
                logger=input.config.logger,
            )
        )

    async def execute(self) -> PostThiesDataControllerOutput:
        try:
            data = await self.use_case.execute()
            if self.use_case.need_to_backup and self.use_case.need_to_sync:
                msg = "THIES data was backed up and synced successfully"
            elif self.use_case.need_to_backup:
                msg = "THIES backup was processed successfully"
            elif self.use_case.need_to_sync:
                msg = "THIES data was synced successfully"
            else:
                msg = "No operation was requested"
            return PostThiesDataControllerOutput(
                message=msg,
                status=HTTPStatus.OK.value,
                metadata={"data": data},  # type: ignore
            )
        except EmptyDataError:
            return PostThiesDataControllerOutput(
                message="No files to upload", status=HTTPStatus.NO_CONTENT.value
            )
        except (AttributeError, NameError, ValueError) as error:
            return PostThiesDataControllerOutput(
                message="An unexpected error occurred during use case initialization.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except FtpClientError as error:
            return PostThiesDataControllerOutput(
                message="Ftp Client initialization fails.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except SharepointClientError as error:
            return PostThiesDataControllerOutput(
                message="Sharepoint Client initialization fails.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        except SharePointFetchingError as error:
            return PostThiesDataControllerOutput(
                message="An error occurred while retrieving file names from Microsoft SharePoint",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except SharePointUploadError as error:
            return PostThiesDataControllerOutput(
                message="An error ocurred while uploading files to RCER Cloud",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except SharePointDirectoryError as error:
            return PostThiesDataControllerOutput(
                message="An error ocurred while extracting folders from Microsoft Sharepoint",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except ThiesFetchingError as error:
            return PostThiesDataControllerOutput(
                message="An error ocurred while retrieving file names from THIES FTP Server.",
                status=HTTPStatus.NO_CONTENT.value,
                metadata={"error": error.__str__()},
            )
        except ThiesConnectionError as error:
            return PostThiesDataControllerOutput(
                message="Unable to connect to THIES Data Logger FTP Server.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        except BackupSourcePathError as error:
            return PostThiesDataControllerOutput(
                message="The specified local backup source path does not exist.",
                status=HTTPStatus.NOT_FOUND.value,
                metadata={"error": error.__str__()},
            )
