from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.services.tasks.controllers.types.update_task_schema import (
    UPDATE_TASK_SCHEMA,
)
from saviialib.libs.zero_dependency.utils.datetime_utils import str_to_datetime
from saviialib.services.tasks.controllers.types.update_task_types import (
    UpdateTaskControllerInput,
)
from saviialib.libs.log_client import (
    LogClient,
    LogClientArgs,
    LogStatus,
    DebugArgs,
)


class UpdateTaskValidator:
    def __init__(self, input: UpdateTaskControllerInput):
        self.input = input
        self.log_client = LogClient(
            LogClientArgs(
                client_name="logging",
                service_name="tasks",
                class_name="update_task_validator",
            )
        )

    def _validate_controller_input(self):
        self.log_client.method_name = "_validate_controller_input"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        SchemaValidatorClient(schema=UPDATE_TASK_SCHEMA).validate(
            {
                "tid": self.input.task.get("tid", ""),
                "title": self.input.task.get("title", ""),
                "deadline": self.input.task.get("deadline", ""),
                "creation": self.input.task.get("creation", ""),
                "execution": self.input.task.get("execution", ""),
                "priority": self.input.task.get("priority", ""),
                "description": self.input.task.get("description", ""),
                "periodicity": self.input.task.get("periodicity", ""),
                "category": self.input.task.get("category", ""),
                "assignee": self.input.task.get("assignee", ""),
                "assignee_email": self.input.task.get("assignee_email", ""),
                "assignee_discord_username": self.input.task.get(
                    "assignee_discord_username", ""
                ),
                "bot_token": self.input.config.bot_token,
                "completed": self.input.completed,
                "task_channel_id": self.input.config.task_channel_id,
            }
        )
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))

    def _validate_date_ordering(self):
        self.log_client.method_name = "_validate_date_ordering"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        # Validate date ordering
        deadline = self.input.task.get("deadline", "")
        creation = self.input.task.get("creation", "")
        execution = self.input.task.get("execution", "")
        dt_format = "%Y-%m-%d"
        deadline_dt = str_to_datetime(deadline, dt_format)
        creation_dt = str_to_datetime(creation, dt_format)
        execution_dt = (
            str_to_datetime(execution, dt_format) if execution else creation_dt
        )
        if not (creation_dt <= execution_dt <= deadline_dt):
            raise ValueError(
                "Invalid date ordering. Must be creation <= execution <= deadline."
            )
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))

    def validate(self):
        self.log_client.method_name = "validate"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        # Validate request schema
        self._validate_controller_input()
        # Validate correct date ordering
        self._validate_date_ordering()
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
