from saviialib.general_types.api.saviia_tasks_api_types import (
    SaviiaTasksConfig,
)
from typing import Dict, Any
from .controllers.create_task import CreateTaskController, CreateTaskControllerInput


class SaviiaTasksAPI:
    def __init__(self, config: SaviiaTasksConfig) -> None:
        self.config = config

    async def create_task(
        self, channel_id: str, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        controller = CreateTaskController(
            CreateTaskControllerInput(self.config, task=task, channel_id=channel_id)
        )
        response = await controller.execute()
        return response.__dict__
