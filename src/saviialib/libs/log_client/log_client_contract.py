# External libraries
from abc import ABC, abstractmethod

# Internal modules
from saviialib.libs.log_client.types.log_client_types import (
    ErrorArgs,
    InfoArgs,
    DebugArgs,
    WarningArgs,
)


class LogClientContract(ABC):
    @abstractmethod
    def info(self, args: InfoArgs):
        pass

    @abstractmethod
    def error(self, args: ErrorArgs):
        pass

    @abstractmethod
    def debug(self, args: DebugArgs):
        pass

    @abstractmethod
    def warning(self, args: WarningArgs):
        pass
