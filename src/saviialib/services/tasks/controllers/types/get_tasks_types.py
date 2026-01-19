from dataclasses import dataclass, field
from typing import Dict
from saviialib.general_types.api.saviia_tasks_api_types import SaviiaTasksConfig


@dataclass
class GetTasksControllerInput:
    config: SaviiaTasksConfig
    channel_id: str
    params: Dict[str, str] = field(default_factory=dict)


@dataclass
class GetTasksControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
