from .types.update_task_types import UpdateTaskUseCaseInput, UpdateTaskUseCaseOutput
from saviialib.libs.log_client import LogClient, LogClientArgs, LogStatus, DebugArgs
from saviialib.libs.notification_client import (
    UpdateNotificationArgs,
    ReactArgs,
    DeleteReactionArgs,
)
from saviialib.services.tasks.presenters import TaskNotificationPresenter


class UpdateTaskUseCase:
    def __init__(self, input: UpdateTaskUseCaseInput) -> None:
        self.logger = LogClient(
            LogClientArgs(service_name="tasks", class_name="update_tasks")
        )
        self.notification_client = input.notification_client
        self.task = input.task
        self.presenter = TaskNotificationPresenter()

    async def execute(self) -> UpdateTaskUseCaseOutput:
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        new_content = self.presenter.to_markdown(self.task)
        task = await self.notification_client.update_notification(
            UpdateNotificationArgs(
                notification_title=self.task.name, new_content=new_content
            )
        )
        if self.task.completed:
            await self.notification_client.react(ReactArgs(task["id"], "✅"))
            await self.notification_client.delete_reaction(
                DeleteReactionArgs(task["id"], "📌")
            )
        else:
            await self.notification_client.react(ReactArgs(task["id"], "📌"))
            await self.notification_client.delete_reaction(
                DeleteReactionArgs(task["id"], "✅")
            )

        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return UpdateTaskUseCaseOutput(
            content=self.task.name,
            description=self.task.description,
            priority=self.task.priority,
            due_date=self.task.due_date,
            completed=self.task.completed,
        )
