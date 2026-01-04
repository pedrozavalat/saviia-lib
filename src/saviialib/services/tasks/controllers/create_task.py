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
    SaviiaTask,
)
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from .types.create_task_schema import CreateTaskSchema
from saviialib.libs.notification_client import (
    NotificationClient,
    NotificationClientInitArgs,
)


class CreateTaskController:
    def __init__(self, input: CreateTaskControllerInput):
        self.init_error = False
        try:
            SchemaValidatorClient(schema=CreateTaskSchema).validate(input.task)
            self.use_case = CreateTaskUseCase(
                CreateTaskUseCaseInput(
                    task=SaviiaTask(
                        name=input.task["name"],
                        description=input.task["description"],
                        due_date=input.task["due_date"],
                        priority=input.task["priority"],
                        assignee=input.task["assignee"],
                        category=input.task["category"],
                        images=input.task.get("images", []),
                    ),
                    notification_client=NotificationClient(
                        NotificationClientInitArgs(
                            client_name="discord_client",
                            api_key=input.config.notification_client_api_key,
                            channel_id=input.channel_id,
                        )
                    ),
                )
            )
        except (ValidationError, KeyError) as error:
            self.init_error = error

    async def execute(self) -> CreateTaskControllerOutput:
        if self.init_error:
            return CreateTaskControllerOutput(
                message="Invalid input data for creating a task.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": self.init_error.__str__()},  # type: ignore
            )
        try:
            output = await self.use_case.execute()
            return CreateTaskControllerOutput(
                message="Task created successfully!",
                status=HTTPStatus.OK.value,
                metadata=output.__dict__,
            )
        except ConnectionError as error:
            return CreateTaskControllerOutput(
                message="An unexpected error ocurred during Discord client connection.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},  # type:ignore
            )
        
        except OSError as error:
            return CreateTaskControllerOutput(
                message="An unexpected error ocurred during task creation.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},  # type:ignore
            )
    