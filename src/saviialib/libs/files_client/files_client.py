from .clients.aiofiles_client import AioFilesClient
from .files_client_contract import FilesClientContract
from .types.files_client_types import FilesClientInitArgs, ReadArgs, WriteArgs


class FilesClient(FilesClientContract):
    CLIENTS = {"aiofiles_client"}

    def __init__(self, args: FilesClientInitArgs) -> None:
        if args.client_name not in FilesClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)

        if args.client_name == "aiofiles_client":
            self.client_obj = AioFilesClient(args)
        self.client_name = args.client_name

    async def read(self, args: ReadArgs):
        """Reads data from a specified source using the provided arguments.

        :param args (ReadArgs): An object containing the parameters required for the read operation.

        :return file: The result of the read operation, as returned by the client object.
        """
        return await self.client_obj.read(args)

    async def write(self, args: WriteArgs):
        return await self.client_obj.write(args)
