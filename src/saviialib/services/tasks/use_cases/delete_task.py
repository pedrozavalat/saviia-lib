from .types.delete_task_types import DeleteTaskUseCaseInput, DeleteTaskUseCaseOutput
from saviialib.libs.log_client import LogClient, LogClientArgs, LogStatus, DebugArgs
from saviialib.libs.notification_client import (
    DeleteNotificationArgs,
)
from saviialib.services.tasks.presenters import TaskNotificationPresenter


class DeleteTaskUseCase:
    def __init__(self, input: DeleteTaskUseCaseInput) -> None:
        self.logger = LogClient(
            LogClientArgs(service_name="tasks", class_name="delete_task")
        )
        self.notification_client = input.notification_client
        self.task_id = input.task_id
        self.presenter = TaskNotificationPresenter()

    async def execute(self) -> DeleteTaskUseCaseOutput:
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        await self.notification_client.delete_notification(
            DeleteNotificationArgs(notification_id=self.task_id)
        )
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return DeleteTaskUseCaseOutput(task_id=self.task_id)
