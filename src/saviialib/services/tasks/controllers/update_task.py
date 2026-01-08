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
from saviialib.libs.calendar_client import CalendarClient, CalendarClientInitArgs

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
        self.calendar_client = CalendarClient(
            CalendarClientInitArgs(
                client_name="todoist_client",
                api_key=input.config.calendar_client_api_key,
            )
        )

    async def _connect_clients(self) -> None:
        await self.notification_client.connect()
        await self.calendar_client.connect()

    async def _close_clients(self) -> None:
        await self.notification_client.close()
        await self.calendar_client.close()

    async def execute(self) -> UpdateTaskControllerOutput:
        try:
            SchemaValidatorClient(schema=UPDATE_TASK_SCHEMA).validate(
                {
                    "config": {
                        "notification_client_api_key": self.input.config.notification_client_api_key,
                        "calendar_client_api_key": self.input.config.calendar_client_api_key
                    },
                    "channel_id": self.input.channel_id,
                }
            )
            await self._connect_clients()
            use_case = UpdateTaskUseCase(
                UpdateTaskUseCaseInput(
                    notification_client=self.notification_client,
                    calendar_client=self.calendar_client
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
