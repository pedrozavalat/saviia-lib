import csv
from asyncio import to_thread

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


class CsvClient(FilesClientContract):
    def __init__(self, args: FilesClientInitArgs):
        self.dir_client = DirectoryClient(DirectoryClientArgs(client_name="os_client"))

    async def read(self, args: ReadArgs) -> str | bytes:
        raise OSError("This method is not implemented yet.")

    async def write(self, args: WriteArgs) -> None:
        file_type = args.file_name.split(".")[-1]
        file_content = args.file_content
        header = file_content[0].keys()
        if file_type == "tsv":
            delimiter = "\t"
        else:  # Default CSV.
            delimiter = ","

        if args.destination_path == "":
            dest_path = self.dir_client.join_paths(args.file_name)
        else:
            dest_path = self.dir_client.join_paths(
                args.destination_path, args.file_name
            )

        with open(dest_path, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header, delimiter=delimiter)  # type: ignore
            await to_thread(writer.writeheader)
            await to_thread(writer.writerows, file_content)  # type: ignore
