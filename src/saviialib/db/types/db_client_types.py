from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DbClientInitArgs:
    """
    Parameters required to create/configure a DB client.

    Keys in this type define the accepted initialization parameters
    (connection settings, credentials, and client options).
    """

    connection_string: str
    client_name: Literal["pyodbc_client"]


@dataclass
class ExecuteArgs:
    """
    Parameters for statements that mutate data (INSERT/UPDATE/DELETE/DDL).

    Keys in this type define the SQL statement and execution options
    (for example, bound values and transactional flags).

    """

    query: str
    params: list = field(default_factory=list)


@dataclass
class FetchAllArgs:
    """
    Parameters for SELECT queries that return multiple rows.

    Keys in this type define the SQL statement and query options
    (for example, bound values and pagination controls).
    """

    query: str
    params: list = field(default_factory=list)


@dataclass
class FetchOneArgs:
    """
    Parameters for SELECT queries that should return a single row.

    Keys in this type define the SQL statement and query options
    (for example, bound values and mapping mode).
    """

    query: str
    params: list = field(default_factory=list)
