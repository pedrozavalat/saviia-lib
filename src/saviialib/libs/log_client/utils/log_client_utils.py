# Internal libraries
from saviialib.libs.log_client.types.log_client_types import LogStatus


def format_message(class_name: str, method_name: str, status: LogStatus, msg: str = '') -> str:
    if msg:
        return f"{class_name}::{method_name}_{status.value}: {msg}"
    return f"{class_name}::{method_name}_{status.value}"
