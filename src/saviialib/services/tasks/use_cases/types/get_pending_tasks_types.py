from dataclasses import dataclass
from saviialib.libs.notification_client import NotificationClient
from saviialib.libs.email_client import EmailClient
from typing import Dict, List


@dataclass
class GetPendingTasksUseCaseInput:
    notification_client: NotificationClient
    email_client: EmailClient


@dataclass
class GetPendingTasksUseCaseOutput:
    overdue: List[Dict[str, str | bool | dict]]
    ontime: List[Dict[str, str | bool | dict]]
