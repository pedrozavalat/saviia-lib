from .types.delete_task_types import (
    DeleteTaskControllerInput,
    DeleteTaskControllerOutput,
)
from http import HTTPStatus
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ValidationError,
)
from saviialib.services.tasks.use_cases.delete_task import DeleteTaskUseCase
from saviialib.services.tasks.use_cases.types.delete_task_types import (
    DeleteTaskUseCaseInput,
)
from .types.delete_task_schema import DELETE_TASK_SCHEMA
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


class DeleteTaskController:
    def __init__(self, input: DeleteTaskControllerInput) -> None:
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

    async def execute(self) -> DeleteTaskControllerOutput:
        self.log_client.method_name = "execute"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        try:
            SchemaValidatorClient(schema=DELETE_TASK_SCHEMA).validate(
                {
                    "task_id": self.input.task_id,
                    "bot_token": self.input.config.bot_token,
                    "task_channel_id": self.input.config.task_channel_id,
                }
            )
            await self._connect_clients()
            use_case = DeleteTaskUseCase(
                DeleteTaskUseCaseInput(
                    task_id=self.input.task_id,
                    notification_client=self.notification_client,
                )
            )
            output = await use_case.execute()
            self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return DeleteTaskControllerOutput(
                message="Task deleted successfully!",
                status=HTTPStatus.OK.value,
                metadata=output.__dict__,
            )
        except ConnectionError as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return DeleteTaskControllerOutput(
                message="An unexpected error ocurred during Discord client connection.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},  # type:ignore
            )
        except NotImplementedError as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return DeleteTaskControllerOutput(
                message="The requested operation is not implemented.",
                status=HTTPStatus.NOT_IMPLEMENTED.value,
                metadata={"error": error.__str__()},  # type: ignore
            )
        except ValidationError as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return DeleteTaskControllerOutput(
                message="Invalid input data for deleting a task.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},  # type: ignore
            )
        finally:
            await self._close_clients()
