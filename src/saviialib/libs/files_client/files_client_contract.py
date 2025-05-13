from abc import ABC, abstractmethod

from .types.files_client_types import ReadArgs, WriteArgs


class FilesClientContract(ABC):
    @abstractmethod
    async def read(self, args: ReadArgs) -> str | bytes:
        pass

    @abstractmethod
    async def write(self, arg: WriteArgs) -> None:
        pass
