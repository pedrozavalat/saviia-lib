from .types.get_tasks_types import GetTasksUseCaseInput, GetTasksUseCaseOutput
from saviialib.libs.log_client import LogClient, LogClientArgs, LogStatus, DebugArgs
from saviialib.services.tasks.presenters import TaskNotificationPresenter


class GetTasksUseCase:
    def __init__(self, input: GetTasksUseCaseInput) -> None:
        self.logger = LogClient(
            LogClientArgs(service_name="tasks", class_name="update_tasks")
        )
        self.params = input.params
        self.notification_client = input.notification_client
        self.presenter = TaskNotificationPresenter()

    async def execute(self) -> GetTasksUseCaseOutput:
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        tasks_notifications = await self.notification_client.list_notifications()
        tasks = self.presenter.to_task_notifications(tasks_notifications, self.params)
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return GetTasksUseCaseOutput(tasks)
