from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class CalendarClientInitArgs:
    client_name: Literal["todoist_client"]
    api_key: str


@dataclass
class CreateEventArgs:
    content: str
    description: str = ""
    priority: Optional[int] = None
    due_date: str = ""


@dataclass
class UpdateEventArgs:
    event_id: str
    content: str
    description: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[str] = None


@dataclass
class DeleteEventArgs:
    event_id: str


@dataclass
class GetEventByIdArgs:
    event_id: str
