from dataclasses import dataclass, field
from saviialib.libs.notification_client import NotificationClient
from typing import Dict, List

@dataclass
class GetTasksUseCaseInput:
    notification_client: NotificationClient
    params: Dict[str, str] = field(default_factory=dict)

@dataclass
class GetTasksUseCaseOutput:
    tasks: List[Dict[str, str | bool | dict]]