from dataclasses import dataclass
from saviialib.services.tasks.entities import SaviiaTask
from saviialib.libs.notification_client import NotificationClient


@dataclass
class CreateTaskUseCaseInput:
    task: SaviiaTask
    notification_client: NotificationClient


@dataclass
class CreateTaskUseCaseOutput:
    content: str
    description: str
    priority: int
    due_date: str
