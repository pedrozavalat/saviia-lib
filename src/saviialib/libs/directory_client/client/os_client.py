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
    async def listdir(path: str) -> list:
        return await asyncio.to_thread(os.listdir, path)

    @staticmethod
    async def isdir(path: str) -> list:
        return await asyncio.to_thread(os.path.isdir, path)
