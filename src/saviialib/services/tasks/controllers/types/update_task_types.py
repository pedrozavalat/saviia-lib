from dataclasses import dataclass, field
from typing import Dict
from saviialib.general_types.api.saviia_tasks_api_types import SaviiaTasksConfig


@dataclass
class UpdateTaskControllerInput:
    config: SaviiaTasksConfig
    channel_id: str


@dataclass
class UpdateTaskControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)