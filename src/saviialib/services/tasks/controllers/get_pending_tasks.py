from http import HTTPStatus
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ValidationError,
)
from .types.get_pending_tasks_schema import GET_PENDING_TASKS_SCHEMA
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.libs.notification_client import (
    NotificationClient,
    NotificationClientInitArgs,
)
from saviialib.services.tasks.use_cases.get_pending_tasks import (
    GetPendingTasksUseCase,
    GetPendingTasksUseCaseInput,
)
from .types.get_pending_tasks_types import (
    GetPendingTasksControllerInput,
    GetPendingTasksControllerOutput,
)
from saviialib.libs.email_client import EmailClient, EmailClientInitArgs


class GetPendingTasksController:
    def __init__(self, input: GetPendingTasksControllerInput) -> None:
        self.input = input
        # Discord channel where the tasks are stored
        self.notification_client = NotificationClient(
            NotificationClientInitArgs(
                client_name="discord_client",
                api_key=self.input.config.bot_token,
                channel_id=self.input.config.task_channel_id,
            )
        )
        self.email_client = EmailClient(
            EmailClientInitArgs(
                client_name="smtplib",
                email_address=input.config.email_address,
                email_password=input.config.email_password,
                smtp_server="smtp.gmail.com",
                smtp_port=587,
            )
        )

    async def _connect_clients(self) -> None:
        await self.notification_client.connect()

    async def _close_clients(self) -> None:
        await self.notification_client.close()

    async def execute(self) -> GetPendingTasksControllerOutput:
        try:
            SchemaValidatorClient(schema=GET_PENDING_TASKS_SCHEMA).validate(
                {
                    "bot_token": self.input.config.bot_token,
                    "task_channel_id": self.input.config.task_channel_id,
                }
            )
            await self._connect_clients()
            use_case = GetPendingTasksUseCase(
                GetPendingTasksUseCaseInput(
                    notification_client=self.notification_client,
                    email_client=self.email_client,
                )
            )
            output = await use_case.execute()
            return GetPendingTasksControllerOutput(
                message="The pending tasks have been successfully extracted.",
                status=HTTPStatus.OK.value,
                metadata=output.__dict__,
            )
        except ConnectionError as error:
            return GetPendingTasksControllerOutput(
                message="An unexpected error ocurred during Discord client connection.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        except (ValidationError, KeyError) as error:
            return GetPendingTasksControllerOutput(
                message="Invalid input data for extracting uncompleted tasks.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        finally:
            await self._close_clients()
