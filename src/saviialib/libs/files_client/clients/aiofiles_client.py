import aiofiles
from saviialib.libs.directory_client.directory_client import (
    DirectoryClient,
    DirectoryClientArgs,
)
from saviialib.libs.files_client.files_client_contract import FilesClientContract
from saviialib.libs.files_client.types.files_client_types import (
    FilesClientInitArgs,
    ReadArgs,
    WriteArgs,
)
import json


class AioFilesClient(FilesClientContract):
    def __init__(self, args: FilesClientInitArgs):
        self.dir_client = DirectoryClient(DirectoryClientArgs(client_name="os_client"))

    async def read(self, args: ReadArgs) -> str | bytes:
        if args.mode == "json":
            async with aiofiles.open(
                args.file_path, "r", encoding=args.encoding or "utf-8"
            ) as file:
                content = await file.read()
                return json.loads(content)

        encoding = None if args.mode == "rb" else args.encoding
        async with aiofiles.open(args.file_path, args.mode, encoding=encoding) as file:
            return await file.read()

    async def write(self, args: WriteArgs) -> None:
        file_path = (
            self.dir_client.join_paths(args.destination_path, args.file_name)
            if args.destination_path
            else args.file_name
        )
        if args.mode == "json":
            async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
                json_str = json.dumps(args.file_content, ensure_ascii=False, indent=2)
                await file.write(json_str)
            return

        async with aiofiles.open(file_path, args.mode) as file:
            await file.write(args.file_content)
