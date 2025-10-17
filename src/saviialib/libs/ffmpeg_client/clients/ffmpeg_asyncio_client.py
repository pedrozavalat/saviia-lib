from saviialib.libs.ffmpeg_client.types.ffmpeg_client_types import (
    FfmpegClientInitArgs,
    RecordPhotoArgs,
    RecordVideoArgs,
)
from saviialib.libs.ffmpeg_client.ffmpeg_client_contract import FfmpegClientContract
from typing import List
import asyncio
import shutil

from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.zero_dependency.utils.datetime_utils import today, datetime_to_str


class FfmpegAsyncioClient(FfmpegClientContract):
    def __init__(self, args: FfmpegClientInitArgs) -> None:
        self.dir_client = DirectoryClient(DirectoryClientArgs("os_client"))

    def _setup_io_args(
        self,
        rtsp_user: str,
        rtsp_pwd: str,
        ip: str,
        dest_path: str,
        record_prefix: str,
        record_type: str,
    ):
        input_arg = f"rtsp://{rtsp_user}:{rtsp_pwd}@{ip}/stream1"
        output_file = (
            record_prefix
            + "_"
            + datetime_to_str(today(), date_format="%m-%d-%Y_%H-%M-%S")
            + f".{record_type}"
        )
        output_arg = self.dir_client.join_paths(dest_path, output_file)
        return input_arg, output_arg

    async def _ensure_ffmpeg_available(self):
        if shutil.which("ffmpeg"):
            return
        install_cmd = ["apk", "add", "ffmpeg"]  # Only for Home Assistant OS
        process = await asyncio.create_subprocess_shell(
            *install_cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stdin=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise ConnectionAbortedError("Failed to install ffmpeg: ", stderr.decode())

    async def _setup_command(
        self, input_arg: str, output_arg: str, extra: dict
    ) -> List[str]:
        await self._ensure_ffmpeg_available()  # Validate ffmpeg module is installed.
        cmd = ["ffmpeg", "-y", "-i", input_arg, output_arg]
        for k, v in extra.values():
            cmd.insert(-1, k)
            cmd.insert(-1, v)
        return list(map(str, cmd))

    async def record_video(self, args: RecordVideoArgs):
        input_arg, output_arg = self._setup_io_args(
            args.rtsp_user,
            args.rtsp_password,
            args.ip_address,
            args.destination_path,
            "Video",
            args.extension,
        )
        cmd = await self._setup_command(
            input_arg, output_arg, extra={"-t": args.duration}
        )
        process = await asyncio.create_subprocess_exec(
            *cmd, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise ConnectionError(
                "Unexpected error while recording the video: ", stderr.decode()
            )

    async def record_photo(self, args: RecordPhotoArgs):
        input_arg, output_arg = self._setup_io_args(
            args.rtsp_user,
            args.rtsp_password,
            args.ip_address,
            args.destination_path,
            "Photo",
            args.extension,
        )
        cmd = await self._setup_command(
            input_arg, output_arg, extra={"-frames:v": args.frames}
        )
        process = await asyncio.create_subprocess_exec(
            *cmd, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise ConnectionError(
                "Unexpected error while recording the photo: ", stderr.decode()
            )
