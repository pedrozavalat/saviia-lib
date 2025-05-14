from abc import ABC, abstractmethod


class DirectoryClientContract(ABC):
    @abstractmethod
    def join_paths(self, *paths: str) -> str:
        pass

    @abstractmethod
    async def path_exists(self, path: str) -> bool:
        pass

    @abstractmethod
    async def listdir(self, path: str) -> list:
        pass

    @abstractmethod
    async def isdir(self, path) -> bool:
        pass
