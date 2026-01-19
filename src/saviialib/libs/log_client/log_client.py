# Internal modules
from saviialib.libs.log_client.log_client_contract import LogClientContract
from saviialib.libs.log_client.logging_client.logging_client import LoggingClient
from saviialib.libs.log_client.types.log_client_types import (
    ErrorArgs,
    InfoArgs,
    LogClientArgs,
    DebugArgs,
    WarningArgs,
)


class LogClient(LogClientContract):
    def __init__(self, args: LogClientArgs):
        clients = {
            "logging": LoggingClient(args),
        }
        if clients.get(args.client_name):
            self.client_name = args.client_name
            self.client_obj = clients[args.client_name]
        else:
            raise KeyError(f"Unsupported client '{args.client_name}'.")

    @property
    def method_name(self):
        return self.client_obj.method_name

    @method_name.setter
    def method_name(self, method_name: str):
        self.client_obj.method_name = method_name

    @property
    def log_history(self):
        return self.client_obj.log_history

    def info(self, args: InfoArgs):
        return self.client_obj.info(args)

    def error(self, args: ErrorArgs):
        return self.client_obj.error(args)

    def debug(self, args: DebugArgs):
        return self.client_obj.debug(args)

    def warning(self, args: WarningArgs):
        return self.client_obj.warning(args)
