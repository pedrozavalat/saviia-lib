from dataclasses import dataclass
from saviialib.services.tasks.entities import SaviiaTask
from saviialib.libs.notification_client import NotificationClient


@dataclass
class UpdateTaskUseCaseInput:
    task: SaviiaTask
    notification_client: NotificationClient


@dataclass
class UpdateTaskUseCaseOutput:
    tid: str
    title: str
    deadline: str
    priority: int
    description: str | None
    periodicity: str | None
    assignee: str | None
    category: str | None
    completed: bool | None