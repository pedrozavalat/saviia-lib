from .clients.aiofiles_client import AioFilesClient
from .clients.csv_client import CsvClient
from .files_client_contract import FilesClientContract
from .types.files_client_types import FilesClientInitArgs, ReadArgs, WriteArgs


class FilesClient(FilesClientContract):
    CLIENTS = {"aiofiles_client", "csv_client"}

    def __init__(self, args: FilesClientInitArgs) -> None:
        if args.client_name not in FilesClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)

        if args.client_name == "aiofiles_client":
            self.client_obj = AioFilesClient(args)
        elif args.client_name == "csv_client":
            self.client_obj = CsvClient(args)

        self.client_name = args.client_name

    async def read(self, args: ReadArgs):
        return await self.client_obj.read(args)

    async def write(self, args: WriteArgs):
        return await self.client_obj.write(args)
