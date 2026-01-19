from .types.create_task_types import (
    CreateTaskControllerInput,
    CreateTaskControllerOutput,
)
from http import HTTPStatus
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ValidationError,
    ExistingNotificationError,
)
from saviialib.services.tasks.use_cases.create_task import CreateTaskUseCase
from saviialib.services.tasks.entities import SaviiaTask
from saviialib.services.tasks.use_cases.types.create_task_types import (
    CreateTaskUseCaseInput,
)
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from .types.create_task_schema import CREATE_TASK_SCHEMA
from saviialib.libs.notification_client import (
    NotificationClient,
    NotificationClientInitArgs,
)


class CreateTaskController:
    def __init__(self, input: CreateTaskControllerInput):
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

    async def execute(self) -> CreateTaskControllerOutput:
        try:
            # SchemaValidatorClient(schema=CREATE_TASK_SCHEMA).validate(self.input.task)
            SchemaValidatorClient(schema=CREATE_TASK_SCHEMA).validate(
                {
                    "task": self.input.task,
                    "config": {
                        "notification_client_api_key": self.input.config.notification_client_api_key
                    },
                    "channel_id": self.input.channel_id,
                }
            )

            await self._connect_clients()
            use_case = CreateTaskUseCase(
                CreateTaskUseCaseInput(
                    task=SaviiaTask(
                        name=self.input.task["name"],
                        description=self.input.task["description"],
                        due_date=self.input.task["due_date"],
                        priority=self.input.task["priority"],
                        assignee=self.input.task["assignee"],
                        category=self.input.task["category"],
                        images=self.input.task.get("images", []),
                    ),
                    notification_client=self.notification_client,
                )
            )
            output = await use_case.execute()
            return CreateTaskControllerOutput(
                message="Task created successfully!",
                status=HTTPStatus.OK.value,
                metadata=output.__dict__,
            )
        except ConnectionError as error:
            return CreateTaskControllerOutput(
                message="An unexpected error ocurred during Discord client connection.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )

        except OSError as error:
            return CreateTaskControllerOutput(
                message="An unexpected error ocurred during task creation.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )

        except ExistingNotificationError as error:
            return CreateTaskControllerOutput(
                message="The task notification already exists.",
                status=HTTPStatus.CONFLICT.value,
                metadata={"error": error.__str__()},
            )
        except (ValidationError, KeyError) as error:
            return CreateTaskControllerOutput(
                message="Invalid input data for creating a task.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},  # type: ignore
            )
        finally:
            await self._close_clients()
