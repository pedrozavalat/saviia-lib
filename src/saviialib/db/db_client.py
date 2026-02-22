from typing import Any, List

from .db_client_contract import DbClientContract
from .types.db_client_types import (
    DbClientInitArgs,
    ExecuteArgs,
    FetchAllArgs,
    FetchOneArgs,
)
from .clients.pyodbc_client import PyODBCClient


class DbClient(DbClientContract):
    CLIENTS = {"pyodbc_client"}

    def __init__(self, args: DbClientInitArgs) -> None:
        if args.client_name not in DbClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)
        if args.client_name == "pyodbc_client":
            self.client_obj = PyODBCClient(args)
        self.client_name = args.client_name

    async def connect(self) -> None:
        return await self.client_obj.connect()

    async def close(self) -> None:
        return await self.client_obj.close()

    async def execute(self, args: ExecuteArgs) -> None:
        return await self.client_obj.execute(args)

    async def fetch_all(self, args: FetchAllArgs) -> List[Any]:
        return await self.client_obj.fetch_all(args)

    async def fetch_one(self, args: FetchOneArgs) -> Any:
        return await self.client_obj.fetch_one(args)
