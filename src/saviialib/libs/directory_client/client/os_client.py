from saviialib.libs.directory_client.directory_client_contract import (
    DirectoryClientContract,
)
import os
import asyncio


class OsClient(DirectoryClientContract):
    @staticmethod
    def join_paths(*paths: str) -> str:
        return os.path.join(*paths)

    @staticmethod
    async def path_exists(path: str) -> bool:
        return await asyncio.to_thread(os.path.exists, path)

    @staticmethod
    async def listdir(path: str, more_info: bool = False) -> list:
        def _listdir_with_size(path):
            items = []
            for name in os.listdir(path):
                full_path = os.path.join(path, name)
                is_dir = os.path.isdir(full_path)
                size = os.stat(full_path).st_size if not is_dir else 0
                items.append((name, size))
            return items
        if more_info:
            return await asyncio.to_thread(_listdir_with_size, path)
        return await asyncio.to_thread(os.listdir, path)

    @staticmethod
    async def isdir(path: str) -> bool:
        return await asyncio.to_thread(os.path.isdir, path)

    @staticmethod
    async def makedirs(path: str) -> None:
        return await asyncio.to_thread(os.makedirs, path, exist_ok=True)
