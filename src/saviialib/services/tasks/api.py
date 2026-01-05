from saviialib.general_types.api.saviia_tasks_api_types import (
    SaviiaTasksConfig,
)
from typing import Dict, Any
from .controllers import (
    CreateTaskController,
    CreateTaskControllerInput,
    GetTasksController,
    GetTasksControllerInput,
    UpdateTaskController,
    UpdateTaskControllerInput,
)


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

    async def update_task(
        self, channel_id: str, task: Dict[str, Any], completed: bool = False
    ) -> Dict[str, Any]:
        controller = UpdateTaskController(
            UpdateTaskControllerInput(self.config, task, channel_id, completed)
        )
        response = await controller.execute()
        return response.__dict__

    async def get_tasks(self, channel_id: str, params: dict = {}) -> Dict[str, Any]:
        controller = GetTasksController(GetTasksControllerInput(
            self.config, channel_id, params
        ))
        response = await controller.execute()
        return response.__dict__
