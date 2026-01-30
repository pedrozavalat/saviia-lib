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
from saviialib.libs.log_client import (
    LogClient,
    LogClientArgs,
    LogStatus,
    DebugArgs,
    ErrorArgs,
)


class UpdateTaskController:
    FIELDS = [
        "tid",
        "title",
        "deadline",
        "priority",
        "description",
        "periodicity",
        "assignee",
        "category",
    ]

    def __init__(self, input: UpdateTaskControllerInput) -> None:
        self.input = input
        self.notification_client = NotificationClient(
            NotificationClientInitArgs(
                client_name="discord_client",
                webhook_url=self.input.webhook_url,
            )
        )
        self.log_client = LogClient(
            LogClientArgs(
                client_name="logging",
                service_name="tasks",
                class_name="update_task_controller",
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

    async def execute(self) -> UpdateTaskControllerOutput:
        self.log_client.method_name = "execute"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        try:
            SchemaValidatorClient(schema=UPDATE_TASK_SCHEMA).validate(
                {
                    "tid": self.input.task.get("tid", ""),
                    "title": self.input.task.get("title", ""),
                    "deadline": self.input.task.get("deadline", ""),
                    "priority": self.input.task.get("priority", ""),
                    "description": self.input.task.get("description", ""),
                    "periodicity": self.input.task.get("periodicity", ""),
                    "category": self.input.task.get("category", ""),
                    "assignee": self.input.task.get("assignee", ""),
                    "webhook_url": self.input.webhook_url,
                    "completed": self.input.completed,
                    "channel_id": self.input.channel_id,
                }
            )
            await self._connect_clients()
            use_case = UpdateTaskUseCase(
                UpdateTaskUseCaseInput(
                    task=SaviiaTask(
                        tid=self.input.task.get("tid", ""),
                        title=self.input.task.get("title", ""),
                        deadline=self.input.task.get("deadline", ""),
                        priority=self.input.task.get("priority", ""),
                        description=self.input.task.get("description", ""),
                        periodicity=self.input.task.get("periodicity", ""),
                        assignee=self.input.task.get("assignee", ""),
                        category=self.input.task.get("category", ""),
                        completed=self.input.completed,
                    ),
                    notification_client=self.notification_client,
                )
            )
            if (
                any(
                    self.input.task.get(field) is None
                    for field in UpdateTaskController.FIELDS
                )
                is True
            ):
                return UpdateTaskControllerOutput(
                    message="All the fields must be provided.",
                    status=HTTPStatus.BAD_REQUEST.value,
                    metadata={
                        "fields": UpdateTaskController.FIELDS  # type: ignore
                    },
                )
            output = await use_case.execute()
            self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return UpdateTaskControllerOutput(
                message="Task updated successfully!",
                status=HTTPStatus.OK.value,
                metadata=output.__dict__,
            )
        except ConnectionError as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return UpdateTaskControllerOutput(
                message="An unexpected error ocurred during Discord client connection.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},  # type:ignore
            )
        except NotImplementedError as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return UpdateTaskControllerOutput(
                message="The requested operation is not implemented.",
                status=HTTPStatus.NOT_IMPLEMENTED.value,
                metadata={"error": error.__str__()},  # type: ignore
            )
        except ValidationError as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return UpdateTaskControllerOutput(
                message="Invalid input data for updating a task.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},  # type: ignore
            )
        finally:
            await self._close_clients()
