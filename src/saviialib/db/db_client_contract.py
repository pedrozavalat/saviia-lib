from abc import ABC, abstractmethod
from typing import Any, List

from .types.db_client_types import ExecuteArgs, FetchAllArgs, FetchOneArgs


class DbClientContract(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def execute(self, args: ExecuteArgs) -> None:
        pass

    @abstractmethod
    def fetch_all(self, args: FetchAllArgs) -> List[Any]:
        pass

    @abstractmethod
    def fetch_one(self, args: FetchOneArgs) -> Any:
        pass
