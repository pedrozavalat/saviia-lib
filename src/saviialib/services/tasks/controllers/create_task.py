from .types.create_task_types import (
    CreateTaskControllerInput,
    CreateTaskControllerOutput,
)
from http import HTTPStatus
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ValidationError,
)
from saviialib.services.tasks.use_cases.create_task import CreateTaskUseCase
from saviialib.services.tasks.use_cases.types.create_task_types import (
    CreateTaskUseCaseInput,
)
from .types.create_task_schema import CREATE_TASK_SCHEMA
from saviialib.services.tasks.entities.task import SaviiaTask
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.libs.notification_client import (
    NotificationClient,
    NotificationClientInitArgs,
)
from saviialib.libs.log_client import (
    LogClient,
    LogClientArgs,
    LogStatus,
    DebugArgs,
    ErrorArgs,
)


class CreateTaskController:
    def __init__(self, input: CreateTaskControllerInput) -> None:
        self.input = input
        self.notification_client = NotificationClient(
            NotificationClientInitArgs(
                client_name="discord_client",
                api_key=self.input.config.bot_token,
                channel_id=self.input.config.task_channel_id,
            )
        )
        self.log_client = LogClient(
            LogClientArgs(
                client_name="logging",
                service_name="tasks",
                class_name="delete_task_controller",
            )
        )

    async def _connect_clients(self) -> None:
        self.log_client.method_name = "_connect_clients"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        await self.notification_client.connect()
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))

    async def _close_clients(self) -> None:
        self.log_client.method_name = "_close_clients"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        await self.notification_client.close()
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))

    async def execute(self) -> CreateTaskControllerOutput:
        self.log_client.method_name = "execute"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        try:
            SchemaValidatorClient(schema=CREATE_TASK_SCHEMA).validate(
                {
                    "title": self.input.task.get("title", ""),
                    "deadline": self.input.task.get("deadline", ""),
                    "priority": self.input.task.get("priority", ""),
                    "description": self.input.task.get("description", ""),
                    "periodicity": self.input.task.get("periodicity", ""),
                    "category": self.input.task.get("category", ""),
                    "assignee": self.input.task.get("assignee", ""),
                    "bot_token": self.input.config.bot_token,
                    "task_channel_id": self.input.config.task_channel_id,
                    "images": self.input.images,
                }
            )
            await self._connect_clients()
            use_case = CreateTaskUseCase(
                CreateTaskUseCaseInput(
                    task=SaviiaTask(
                        title=self.input.task.get("title", ""),
                        deadline=self.input.task.get("deadline", ""),
                        priority=self.input.task.get("priority", ""),
                        description=self.input.task.get("description", ""),
                        periodicity=self.input.task.get("periodicity", ""),
                        assignee=self.input.task.get("assignee", ""),
                        category=self.input.task.get("category", ""),
                        completed=False,  # By default, the task isn't completed...
                        images=self.input.images,
                    ),
                    notification_client=self.notification_client,
                )
            )
            output = await use_case.execute()
            self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return CreateTaskControllerOutput(
                message="Task created successfully!",
                status=HTTPStatus.OK.value,
                metadata=output.__dict__,
            )
        except ConnectionError as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return CreateTaskControllerOutput(
                message="An unexpected error ocurred during Discord client connection.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        except NotImplementedError as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return CreateTaskControllerOutput(
                message="The requested operation is not implemented.",
                status=HTTPStatus.NOT_IMPLEMENTED.value,
                metadata={"error": error.__str__()},
            )
        except ValidationError as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return CreateTaskControllerOutput(
                message="Invalid input data for deleting a task.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except OSError as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return CreateTaskControllerOutput(
                message="An unexpected error ocurred relating to the Operative System",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        finally:
            await self._close_clients()
