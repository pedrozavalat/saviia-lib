from dataclasses import dataclass, field
from typing import Any


@dataclass
class DbClientInitArgs:
    connection_string: str
    client_name: str = "pyodbc_client"


@dataclass
class ExecuteArgs:
    query: str
    params: list = field(default_factory=list)


@dataclass
class FetchAllArgs:
    query: str
    params: list = field(default_factory=list)


@dataclass
class FetchOneArgs:
    query: str
    params: list = field(default_factory=list)
