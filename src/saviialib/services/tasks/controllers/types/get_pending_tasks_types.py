from dataclasses import dataclass, field
from typing import Dict
from saviialib.general_types.api.saviia_tasks_api_types import SaviiaTasksConfig


@dataclass
class GetPendingTasksControllerInput:
    config: SaviiaTasksConfig
    download: bool = False
    notify: bool = False


@dataclass
class GetPendingTasksControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
