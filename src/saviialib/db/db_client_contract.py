from abc import ABC, abstractmethod
from typing import Any, List

from .types.db_client_types import ExecuteArgs, FetchAllArgs, FetchOneArgs


class DbClientContract(ABC):
    @abstractmethod
    def connect(self) -> None:
        """Open the database connection.

        Returns:
            None: The connection is initialized and ready for operations.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the active database connection.

        Returns:
            None: The connection is closed and resources are released.
        """
        pass

    @abstractmethod
    def execute(self, args: ExecuteArgs) -> None:
        """Execute a non-select SQL statement.

        Args:
            args: Execution payload with:
                - query (str): SQL statement to run.
                - params (list): Positional parameters bound to the query.

        Returns:
            None: The statement is executed without returning rows.
        """
        pass

    @abstractmethod
    def fetch_all(self, args: FetchAllArgs) -> List[Any]:
        """Execute a query and return all matching rows.

        Args:
            args: Query payload with:
                - query (str): SQL statement to run.
                - params (list): Positional parameters bound to the query.

        Returns:
            List[Any]: All rows returned by the query.
        """
        pass

    @abstractmethod
    def fetch_one(self, args: FetchOneArgs) -> Any:
        """Execute a query and return a single row.

        Args:
            args: Query payload with:
                - query (str): SQL statement to run.
                - params (list): Positional parameters bound to the query.

        Returns:
            Any: The first row returned by the query, or ``None`` when no row exists.
        """
        pass
