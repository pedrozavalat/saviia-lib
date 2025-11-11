from .client.os_client import OsClient
from .directory_client_contract import DirectoryClientContract
from .types.directory_client_types import DirectoryClientArgs
from typing import Iterator


class DirectoryClient(DirectoryClientContract):
    CLIENTS = {"os_client"}

    def __init__(self, args: DirectoryClientArgs) -> None:
        if args.client_name not in DirectoryClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)

        if args.client_name == "os_client":
            self.client_obj = OsClient()
        self.client_name = args.client_name

    def join_paths(self, *paths: str) -> str:
        return self.client_obj.join_paths(*paths)

    async def path_exists(self, path: str) -> bool:
        return await self.client_obj.path_exists(path)

    async def listdir(self, path: str, more_info: bool = False) -> list:
        return await self.client_obj.listdir(path, more_info)

    async def isdir(self, path: str) -> bool:
        return await self.client_obj.isdir(path)

    async def makedirs(self, path: str) -> None:
        return await self.client_obj.makedirs(path)

    async def remove_file(self, path: str) -> None:
        return await self.client_obj.remove_file(path)

    async def walk(self, path: str) -> Iterator:
        return await self.client_obj.walk(path)

    def relative_path(self, full_path: str, base_folder: str):
        return self.client_obj.relative_path(full_path, base_folder)

    def get_basename(self, path: str):
        return self.client_obj.get_basename(path)
