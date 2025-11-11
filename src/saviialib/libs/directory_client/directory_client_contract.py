from abc import ABC, abstractmethod
from typing import Iterator


class DirectoryClientContract(ABC):
    @abstractmethod
    def join_paths(self, *paths: str) -> str:
        pass

    @abstractmethod
    async def path_exists(self, path: str) -> bool:
        pass

    @abstractmethod
    async def listdir(self, path: str, more_info: bool = False) -> list:
        pass

    @abstractmethod
    async def isdir(self, path) -> bool:
        pass

    @abstractmethod
    async def makedirs(self, path: str) -> None:
        pass

    @abstractmethod
    async def remove_file(self, path: str) -> None:
        pass

    @abstractmethod
    async def walk(self, path: str) -> Iterator:
        pass

    @abstractmethod
    def relative_path(self, full_path: str, base_folder: str):
        pass

    @abstractmethod
    def get_basename(self, path: str):
        pass
