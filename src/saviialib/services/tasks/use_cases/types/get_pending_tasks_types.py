from dataclasses import dataclass
from saviialib.libs.notification_client import NotificationClient
from saviialib.libs.email_client import EmailClient
from saviialib.libs.directory_client import DirectoryClient
from typing import Dict, List


@dataclass
class GetPendingTasksUseCaseInput:
    notification_client: NotificationClient
    email_client: EmailClient
    dir_client: DirectoryClient
    local_backup_path: str = ""
    download: bool = False
    notify: bool = False


@dataclass
class GetPendingTasksUseCaseOutput:
    overdue: List[Dict[str, str | bool | dict]]
    ontime: List[Dict[str, str | bool | dict]]
