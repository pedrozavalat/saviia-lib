from .types.update_task_types import (
    UpdateTaskControllerInput,
    UpdateTaskControllerOutput,
)
from http import HTTPStatus
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ValidationError,
)
from saviialib.services.tasks.entities import SaviiaTask
from saviialib.services.tasks.use_cases.update_task import UpdateTaskUseCase
from saviialib.services.tasks.use_cases.types.update_task_types import (
    UpdateTaskUseCaseInput,
)
from .types.update_task_schema import UPDATE_TASK_SCHEMA
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.libs.notification_client import (
    NotificationClient,
    NotificationClientInitArgs,
)


class UpdateTaskController:
    def __init__(self, input: UpdateTaskControllerInput) -> None:
        self.input = input
        self.notification_client = NotificationClient(
            NotificationClientInitArgs(
                client_name="discord_client",
                api_key=self.input.config.notification_client_api_key,
                channel_id=self.input.channel_id,
            )
        )

    async def _connect_clients(self) -> None:
        await self.notification_client.connect()

    async def _close_clients(self) -> None:
        await self.notification_client.close()

    async def execute(self) -> UpdateTaskControllerOutput:
        try:
            SchemaValidatorClient(schema=UPDATE_TASK_SCHEMA).validate(
                {
                    "task": self.input.task,
                    "config": {
                        "notification_client_api_key": self.input.config.notification_client_api_key
                    },
                    "channel_id": self.input.channel_id,
                    "completed": self.input.completed,
                }
            )
            await self._connect_clients()
            use_case = UpdateTaskUseCase(
                UpdateTaskUseCaseInput(
                    task=SaviiaTask(
                        name=self.input.task["name"],
                        description=self.input.task["description"],
                        due_date=self.input.task["due_date"],
                        priority=self.input.task["priority"],
                        assignee=self.input.task["assignee"],
                        category=self.input.task["category"],
                        images=self.input.task.get("images", []),
                        completed=self.input.completed,
                    ),
                    notification_client=self.notification_client,
                )
            )
            output = await use_case.execute()
            return UpdateTaskControllerOutput(
                message="Task updated successfully!",
                status=HTTPStatus.OK.value,
                metadata=output.__dict__,
            )
        except ConnectionError as error:
            return UpdateTaskControllerOutput(
                message="An unexpected error ocurred during Discord client connection.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},  # type:ignore
            )
        except (ValidationError, KeyError) as error:
            return UpdateTaskControllerOutput(
                message="Invalid input data for creating a task.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},  # type: ignore
            )
        finally:
            await self._close_clients()
