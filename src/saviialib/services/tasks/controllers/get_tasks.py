from .types.get_tasks_types import GetTasksControllerInput, GetTasksControllerOutput
from http import HTTPStatus
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ValidationError,
)
from saviialib.services.tasks.entities import SaviiaTask
from .types.get_tasks_schema import GET_TASKS_SCHEMA
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.libs.notification_client import (
    NotificationClient,
    NotificationClientInitArgs,
)

from saviialib.services.tasks.use_cases.get_tasks import (
    GetTasksUseCase,
    GetTasksUseCaseInput,
)


class GetTasksController:
    def __init__(self, input: GetTasksControllerInput) -> None:
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

    async def execute(self) -> GetTasksControllerOutput:
        try:
            SchemaValidatorClient(schema=GET_TASKS_SCHEMA).validate(
                {
                    "config": {
                        "notification_client_api_key": self.input.config.notification_client_api_key
                    },
                    "channel_id": self.input.channel_id,
                    "params": self.input.params,
                }
            )
            await self._connect_clients()
            use_case = GetTasksUseCase(
                GetTasksUseCaseInput(
                    notification_client=self.notification_client,
                    params=self.input.params
                )
            )
            output = await use_case.execute()
            return GetTasksControllerOutput(
                message="The service works operates successfully",
                status=HTTPStatus.OK.value,
                metadata=output.__dict__,
            )
        except ConnectionError as error:
            return GetTasksControllerOutput(
                message="An unexpected error ocurred during Discord client connection.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},  
            )
        except (ValidationError, KeyError) as error:
            return GetTasksControllerOutput(
                message="Invalid input data for creating a task.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},  
            )
        finally:
            await self._close_clients()
