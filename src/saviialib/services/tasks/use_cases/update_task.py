from .types.update_task_types import UpdateTaskUseCaseInput, UpdateTaskUseCaseOutput
from saviialib.libs.log_client import LogClient, LogClientArgs, LogStatus, DebugArgs
from saviialib.libs.notification_client import (
    UpdateNotificationArgs,
    FindNotificationArgs,
)
from saviialib.services.tasks.presenters import TaskNotificationPresenter


class UpdateTaskUseCase:
    def __init__(self, input: UpdateTaskUseCaseInput) -> None:
        self.logger = LogClient(
            LogClientArgs(service_name="tasks", class_name="update_tasks")
        )
        self.notification_client = input.notification_client
        self.new_task = input.task
        self.presenter = TaskNotificationPresenter()

    async def execute(self) -> UpdateTaskUseCaseOutput:
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        old_task = await self.notification_client.find_notification(
            FindNotificationArgs(notification_id=self.new_task.tid)
        )
        old_task_dict = self.presenter.to_dict(old_task["content"])
        new_task_dict = {}
        # Update content dict with obligatory fields
        new_task_dict["title"] = (
            self.new_task.title
            if self.new_task.title is not None
            else old_task_dict.get("title", "")
        )
        new_task_dict["deadline"] = (
            self.new_task.deadline
            if self.new_task.deadline is not None
            else old_task_dict.get("deadline", "")
        )
        new_task_dict["priority"] = (
            str(self.new_task.priority)
            if self.new_task.priority is not None
            else old_task_dict.get("priority", "")
        )
        new_task_dict["periodicity"] = (
            self.new_task.periodicity
            if self.new_task.periodicity is not None
            else old_task_dict.get("periodicity", "")
        )
        new_task_dict["assignee"] = (
            self.new_task.assignee
            if self.new_task.assignee is not None
            else old_task_dict.get("assignee", "")
        )
        new_task_dict["category"] = (
            self.new_task.category
            if self.new_task.category is not None
            else old_task_dict.get("category", "")
        )
        new_task_dict["description"] = (
            self.new_task.description
            if self.new_task.description is not None
            else old_task_dict.get("description", "")
        )
        new_task_dict["completed"] = self.new_task.completed
        content_markdown = self.presenter.to_markdown(new_task_dict)
        await self.notification_client.update_notification(
            UpdateNotificationArgs(
                notification_id=self.new_task.tid,
                new_content=content_markdown,
            )
        )
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return UpdateTaskUseCaseOutput(
            tid=self.new_task.tid,
            title=self.new_task.title,
            deadline=self.new_task.deadline,
            priority=self.new_task.priority,
            description=self.new_task.description,
            periodicity=self.new_task.periodicity,
            assignee=self.new_task.assignee,
            category=self.new_task.category,
            completed=self.new_task.completed,
        )
