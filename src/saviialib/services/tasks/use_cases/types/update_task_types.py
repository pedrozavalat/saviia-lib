from dataclasses import dataclass
from saviialib.services.tasks.entities import SaviiaTask
from saviialib.libs.notification_client import NotificationClient
from saviialib.libs.calendar_client import CalendarClient

@dataclass
class UpdateTaskUseCaseInput:
    notification_client: NotificationClient
    calendar_client: CalendarClient


@dataclass
class UpdateTaskUseCaseOutput:
    content: str 
    description: str 
    priority: int
    due_date: str
    completed: bool