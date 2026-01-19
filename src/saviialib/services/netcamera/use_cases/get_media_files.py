from .types.get_media_files_types import (
    GetMediaFilesUseCaseInput,
    GetMediaFilesUseCaseOutput,
)
from saviialib.libs.ffmpeg_client import (
    FfmpegClient,
    FfmpegClientInitArgs,
    RecordVideoArgs,
    RecordPhotoArgs,
)
from saviialib.libs.zero_dependency.utils.strings_utils import are_equal
from typing import Tuple, Dict
from saviialib.libs.directory_client.directory_client import (
    DirectoryClient,
    DirectoryClientArgs,
)
from saviialib.general_types.error_types.api.saviia_netcamera_error_types import (
    NetcameraConnectionError,
)


class GetMediaFilesUseCase:
    def __init__(self, input: GetMediaFilesUseCaseInput) -> None:
        self.ffmpeg_client = FfmpegClient(
            FfmpegClientInitArgs(
                client_name="ffmpeg_asyncio",
            )
        )
        self.dir_client = DirectoryClient(DirectoryClientArgs("os_client"))
        self.user = input.username
        self.pwd = input.password
        self.cameras: Dict[str, Tuple[str, int]] = input.cameras
        self.protocol = input.protocol
        self.logger = input.logger
        self.dest_path = input.destination_path

    async def _retieve_with_rtsp(self):
        for name, conn in self.cameras.items():
            ip, port = conn
            dest_path = self.dir_client.join_paths(self.dest_path, name)
            try:
                # Extraction of photo files into dest_path dir.
                await self.ffmpeg_client.record_photo(
                    RecordPhotoArgs(
                        ip_address=ip,
                        port=str(port),
                        destination_path=dest_path,
                        rtsp_user=self.user,
                        rtsp_password=self.pwd,
                        extension="jpg",
                        frames=1,
                    )
                )
                # Extraction of video files into dest_path dir.
                await self.ffmpeg_client.record_video(
                    RecordVideoArgs(
                        destination_path=dest_path,
                        ip_address=ip,
                        port=str(port),
                        rtsp_user=self.user,
                        rtsp_password=self.pwd,
                        extension="mp3",
                        duration=10,
                    )
                )
            except ConnectionError as error:
                raise NetcameraConnectionError(reason=error)

    async def execute(self) -> GetMediaFilesUseCaseOutput:
        if are_equal(self.protocol, "rtsp"):
            await self._retieve_with_rtsp()
        else:
            raise NotImplementedError(
                f"The media files extraction with {self.protocol} is not implemented yet."
            )
        return GetMediaFilesUseCaseOutput()
