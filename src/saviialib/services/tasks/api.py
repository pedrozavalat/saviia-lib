from typing import Dict, Any
from .controllers import (
    UpdateTaskController,
    UpdateTaskControllerInput,
    DeleteTaskController,
    DeleteTaskControllerInput,
)


class SaviiaTasksAPI:
    def __init__(self) -> None:
        pass

    async def update_task(
        self,
        webhook_url: str,
        task: Dict[str, Any],
        completed: bool,
        channel_id: str = "",
    ) -> Dict[str, Any]:
        controller = UpdateTaskController(
            UpdateTaskControllerInput(task, webhook_url, completed, channel_id)
        )
        response = await controller.execute()
        return response.__dict__

    async def delete_task(
        self, webhook_url: str, task_id: str, channel_id: str = ""
    ) -> Dict[str, Any]:
        controller = DeleteTaskController(
            DeleteTaskControllerInput(task_id, webhook_url, channel_id)
        )
        response = await controller.execute()
        return response.__dict__
