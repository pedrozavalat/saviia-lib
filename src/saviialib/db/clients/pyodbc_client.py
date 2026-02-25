import pyodbc
from typing import Any, List

from saviialib.db.db_client_contract import DbClientContract
from saviialib.db.types.db_client_types import (
    DbClientInitArgs,
    ExecuteArgs,
    FetchAllArgs,
    FetchOneArgs,
)


class PyODBCClient(DbClientContract):
    def __init__(self, args: DbClientInitArgs) -> None:
        self.connection_string = args.connection_string
        self.connection: pyodbc.Connection | None = None
        self.cursor: pyodbc.Cursor | None = None

    async def connect(self) -> None:
        if self.connection:
            return
        try:
            self.connection = pyodbc.connect(self.connection_string)
            self.cursor = self.connection.cursor()
        except pyodbc.Error as error:
            raise ConnectionError(f"Failed to connect to database: {error}") from error

    async def close(self) -> None:
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None

    async def execute(self, args: ExecuteArgs) -> None:
        if not self.cursor:
            raise ConnectionError("Not connected to a database. Call connect() first.")
        try:
            self.cursor.execute(args.query, args.params)
            self.connection.commit()  # type: ignore
        except pyodbc.Error as error:
            raise RuntimeError(f"Failed to execute query: {error}") from error

    async def fetch_all(self, args: FetchAllArgs) -> List[Any]:
        if not self.cursor:
            raise ConnectionError("Not connected to a database. Call connect() first.")
        try:
            self.cursor.execute(args.query, args.params)
            return self.cursor.fetchall()
        except pyodbc.Error as error:
            raise RuntimeError(f"Failed to fetch results: {error}") from error

    async def fetch_one(self, args: FetchOneArgs) -> Any:
        if not self.cursor:
            raise ConnectionError("Not connected to a database. Call connect() first.")
        try:
            self.cursor.execute(args.query, args.params)
            return self.cursor.fetchone()
        except pyodbc.Error as error:
            raise RuntimeError(f"Failed to fetch result: {error}") from error
