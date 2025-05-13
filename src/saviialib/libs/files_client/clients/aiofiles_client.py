import aiofiles

from saviialib.libs.files_client.files_client_contract import FilesClientContract
from saviialib.libs.files_client.types.files_client_types import (
    FilesClientInitArgs,
    ReadArgs,
    WriteArgs,
)


class AioFilesClient(FilesClientContract):
    def __init__(self, args: FilesClientInitArgs):
        pass

    async def read(self, args: ReadArgs) -> str | bytes:
        encoding = None if args.mode == "rb" else args.encoding
        async with aiofiles.open(args.file_path, args.mode, encoding=encoding) as file:
            return await file.read()

    async def write(self, args: WriteArgs) -> None:
        return None
