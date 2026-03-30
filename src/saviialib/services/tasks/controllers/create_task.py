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
from saviialib.services.tasks.entities.task import SaviiaTask
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
from .validators.create_task_validator import CreateTaskValidator
from saviialib.libs.email_client import EmailClient, EmailClientInitArgs


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
                class_name="create_task_controller",
            )
        )
        self.validator = CreateTaskValidator(input)
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
            self.validator.validate()
            await self._connect_clients()
            use_case = CreateTaskUseCase(
                CreateTaskUseCaseInput(
                    task=SaviiaTask(
                        title=self.input.task.get("title", ""),
                        deadline=self.input.task.get("deadline", ""),
                        creation=self.input.task.get("creation", ""),
                        execution=self.input.task.get("execution", ""),
                        priority=self.input.task.get("priority", ""),
                        description=self.input.task.get("description", ""),
                        periodicity=self.input.task.get("periodicity", ""),
                        assignee=self.input.task.get("assignee", ""),
                        assignee_email=self.input.task.get("assignee_email", ""),
                        assignee_discord_username=self.input.task.get(
                            "assignee_discord_username", ""
                        ),
                        category=self.input.task.get("category", ""),
                        completed=False,  # By default, the task isn't completed...
                        images=self.input.images,
                    ),
                    notification_client=self.notification_client,
                    email_client=self.email_client,
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
        except (ValidationError, ValueError) as error:
            self.log_client.error(ErrorArgs(LogStatus.ERROR, {"msg": error.__str__()}))
            return CreateTaskControllerOutput(
                message="Invalid input data for creating a task.",
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
