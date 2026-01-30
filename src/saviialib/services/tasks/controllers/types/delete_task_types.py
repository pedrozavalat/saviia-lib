from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class DeleteTaskControllerInput:
    task_id: str
    webhook_url: str
    channel_id: str = ""


@dataclass
class DeleteTaskControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
