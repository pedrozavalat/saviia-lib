from .ffmpeg_client_contract import FfmpegClientContract
from .types.ffmpeg_client_types import (
    RecordPhotoArgs,
    RecordVideoArgs,
    FfmpegClientInitArgs,
)
from .clients.ffmpeg_asyncio_client import FfmpegAsyncioClient


class FfmpegClient(FfmpegClientContract):
    CLIENTS = {"ffmpeg_asyncio"}

    def __init__(self, args: FfmpegClientInitArgs) -> None:
        if args.client_name not in FfmpegClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)
        if args.client_name == "ffmpeg_asyncio":
            self.client_obj = FfmpegAsyncioClient(args)
        self.client_name = args.client_name

    def record_photo(self, args: RecordPhotoArgs):
        return self.client_obj.record_photo(args)

    def record_video(self, args: RecordVideoArgs):
        return self.client_obj.record_video(args)
