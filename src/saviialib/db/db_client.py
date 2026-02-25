from typing import Any, List

from .db_client_contract import DbClientContract
from .types.db_client_types import (
    DbClientInitArgs,
    ExecuteArgs,
    FetchAllArgs,
    FetchOneArgs,
)


class DbClient(DbClientContract):
    CLIENTS = {"pyodbc_client"}

    def __init__(self, args: DbClientInitArgs) -> None:
        if args.client_name not in DbClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)
        if args.client_name == "pyodbc_client":
            self.client_obj = None  # Not supported Yet
        self.client_name = args.client_name

    async def connect(self) -> None:
        # TODO: Not implemented yet
        return 

    async def close(self) -> None:
        # TODO: Not implemented yet
        return

    async def execute(self, args: ExecuteArgs) -> None:
        # TODO: Not implemented yet
        return 

    async def fetch_all(self, args: FetchAllArgs) -> List[Any]:
        # TODO: Not implemented yet
        return [()]

    async def fetch_one(self, args: FetchOneArgs) -> Any:
        # TODO: Not implemented yet
        return [()]
