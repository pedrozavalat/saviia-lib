from typing import Dict, Any
from saviialib.general_types.api.saviia_tasks_api_types import SaviiaTasksConfig
from .controllers import (
    CreateTaskController,
    CreateTaskControllerInput,
    UpdateTaskController,
    UpdateTaskControllerInput,
    DeleteTaskController,
    DeleteTaskControllerInput,
    GetTasksController,
    GetTasksControllerInput,
)


class SaviiaTasksAPI:
    def __init__(self, config: SaviiaTasksConfig) -> None:
        self.config = config

    async def update_task(
        self, task: Dict[str, Any], completed: bool
    ) -> Dict[str, Any]:
        """
        Updates a task with the provided data and completion status.

        :param self: The instance of the API service class
        :param task: Dictionary containing task data to update
        :type task: Dict[str, Any]
        :param completed: Boolean flag indicating if the task is completed
        :type completed: bool
        :return: A dictionary representation of the update response
        :rtype: Dict[str, Any]
        """
        controller = UpdateTaskController(
            UpdateTaskControllerInput(task, completed, self.config)
        )
        response = await controller.execute()
        return response.__dict__

    async def delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Deletes a task by its ID.

        :param self: The instance of the API service class
        :param task_id: The unique identifier of the task to delete
        :type task_id: str
        :return: A dictionary representation of the delete response
        :rtype: Dict[str, Any]
        """
        controller = DeleteTaskController(
            DeleteTaskControllerInput(task_id, self.config)
        )
        response = await controller.execute()
        return response.__dict__

    async def create_task(self, task: dict, images: list = []) -> Dict[str, Any]:
        """
        Creates a new task with the provided task data and associated images.

        :param self: The instance of the API service class
        :param task: Dictionary containing task data
        :type task: dict
        :param images: List of images associated with the task
        :type images: list
        :return: A dictionary representation of the create response
        :rtype: Dict[str, Any]
        """
        controller = CreateTaskController(
            CreateTaskControllerInput(task, images, self.config)
        )
        response = await controller.execute()
        return response.__dict__

    async def get_tasks(self, params={}) -> Dict[str, Any]:
        """
        Retrieves a list of tasks based on the provided parameters.

        :param self: The instance of the API service class
        :param params: Optional dictionary containing filter parameters for task retrieval (default: {})

            - `sort` (str): Order results by `asc` or `desc`.
            - `completed` (bool): Filter tasks by completion status.
            - `fields` (list): Specify which fields to include in the response. Must include `title` and `due_date`.
            - `after` and `before` (str): Filter tasks by timestamp ranges.
        :return: A dictionary representation of the tasks response containing task data
        """
        controller = GetTasksController(GetTasksControllerInput(self.config, params))
        response = await controller.execute()
        return response.__dict__
