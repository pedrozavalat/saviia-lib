from dataclasses import dataclass
from saviialib.libs.notification_client import NotificationClient
from typing import Dict, List


@dataclass
class GetPendingTasksUseCaseInput:
    notification_client: NotificationClient


@dataclass
class GetPendingTasksUseCaseOutput:
    overdue: List[Dict[str, str | bool | dict]]
    ontime: List[Dict[str, str | bool | dict]]
