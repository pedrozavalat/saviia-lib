from dataclasses import dataclass
from saviialib.libs.notification_client import NotificationClient
from saviialib.services.tasks.entities.task import SaviiaTask


@dataclass
class CreateTaskUseCaseInput:
    task: SaviiaTask
    notification_client: NotificationClient


@dataclass
class CreateTaskUseCaseOutput:
    task_id: str
