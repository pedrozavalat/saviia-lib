from abc import ABC, abstractmethod
from .types.ffmpeg_client_types import RecordPhotoArgs, RecordVideoArgs


class FfmpegClientContract(ABC):
    @abstractmethod
    async def record_photo(self, args: RecordPhotoArgs):
        pass

    @abstractmethod
    async def record_video(self, args: RecordVideoArgs):
        pass
