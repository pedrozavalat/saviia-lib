from dataclasses import dataclass
from saviialib.libs.notification_client import NotificationClient


@dataclass
class DeleteTaskUseCaseInput:
    task_id: str
    notification_client: NotificationClient


@dataclass
class DeleteTaskUseCaseOutput:
    task_id: str
    