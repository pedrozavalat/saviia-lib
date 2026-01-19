# External libraries
import logging

# Internal modules
from saviialib.libs.log_client.utils.log_client_utils import format_message
from saviialib.libs.log_client.log_client_contract import LogClientContract
from saviialib.libs.log_client.types.log_client_types import (
    ErrorArgs,
    InfoArgs,
    LogClientArgs,
    DebugArgs,
    WarningArgs,
)

from saviialib.libs.zero_dependency.utils.datetime_utils import today, datetime_to_str


class LoggingClient(LogClientContract):
    def __init__(self, args: LogClientArgs):
        log_format = "{message}"
        logging.basicConfig(format=log_format, level=logging.INFO, style="{")
        self.class_name = args.class_name
        self.method_name = args.method_name
        self.active_record = args.active_record
        self.log_history = []

    def _save_to_history(self, meta: dict):
        self.log_history.append(
            f"[{datetime_to_str(today(), date_format='%m-%d-%Y %H:%M:%S')}][{self.class_name}] {meta.get('msg', '')}"
        )

    def info(self, args: InfoArgs) -> None:
        if self.active_record:
            self._save_to_history(args.metadata)
        return logging.info(
            format_message(self.class_name, self.method_name, args.status)
        )

    def error(self, args: ErrorArgs) -> None:
        if self.active_record:
            self._save_to_history(args.metadata)
        return logging.error(
            format_message(self.class_name, self.method_name, args.status)
        )

    def debug(self, args: DebugArgs) -> None:
        if self.active_record:
            self._save_to_history(args.metadata)
        return logging.debug(
            format_message(self.class_name, self.method_name, args.status)
        )

    def warning(self, args: WarningArgs) -> None:
        if self.active_record:
            self._save_to_history(args.metadata)
        return logging.warning(
            format_message(self.class_name, self.method_name, args.status)
        )
