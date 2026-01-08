from .types.create_task_types import CreateTaskUseCaseInput, CreateTaskUseCaseOutput
from saviialib.libs.log_client import LogClient, LogClientArgs, LogStatus, DebugArgs
from saviialib.libs.notification_client import (
    NotifyArgs,
    ReactArgs,
    FindNotificationByContentArgs,
    UpdateNotificationArgs,
)
from saviialib.libs.calendar_client import CreateEventArgs
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.files_client import (
    FilesClient,
    FilesClientInitArgs,
    WriteArgs,
)
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ExistingNotificationError,
)
from saviialib.services.tasks.presenters import TaskNotificationPresenter


class CreateTaskUseCase:
    def __init__(self, input: CreateTaskUseCaseInput) -> None:
        self.task = input.task
        self.notification_client = input.notification_client
        self.calendar_client = input.calendar_client
        self.log_client = LogClient(
            LogClientArgs(service_name="tasks", class_name="create_tasks")
        )
        self.dir_client = DirectoryClient(DirectoryClientArgs("os_client"))
        self.files_client = FilesClient(FilesClientInitArgs("aiofiles_client"))
        self.presenter = TaskNotificationPresenter()

    async def execute(self) -> CreateTaskUseCaseOutput:
        self.log_client.method_name = "execute"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        # Preprocess task content
        files = []
        embeds = []
        if self.task.images:
            await self.dir_client.makedirs("tmp")
            for image in self.task.images:
                await self.files_client.write(
                    WriteArgs(
                        file_name=f"{image['name']}",
                        file_content=image["data"],
                        mode="jpeg",
                        destination_path="tmp",
                    )
                )
                files.append(f"./tmp/{image['name']}")
                embeds.append({"image": {"url": f"attachment://{image['name']}"}})

        # Check if notification is already created at the discord channel
        exists = await self.notification_client.find_notification_by_content(
            FindNotificationByContentArgs(content=self.task.name, reactions=["📌"])
        )
        if exists:
            self.log_client.debug(DebugArgs(LogStatus.ALERT))
            raise ExistingNotificationError(
                reason=f"A task with the name '{self.task.name}' already exists."
            )

        # Create the new task in the #created-tasks channel at Discord
        new_task = await self.notification_client.notify(
            NotifyArgs(
                content=self.presenter.to_markdown(self.task),
                embeds=embeds,
                files=files,
            )
        )
        task_id = new_task["id"]  # Discord Id in this case.
        # Create the related event in Todoist
        new_event = await self.calendar_client.create_event(
            CreateEventArgs(
                content=self.task.name,
                description=self.task.description,
                priority=self.task.priority,
                due_date=self.task.due_date,
            )
        )
        event_id = new_event["eid"]
        # Update the created task adding the task_id in the content
        await self.notification_client.update_notification(
            UpdateNotificationArgs(
                notification_id=task_id,
                new_content=self.presenter.to_markdown(self.task, f"{event_id}-{task_id}"),
            )
        )
        # Mark as need to action
        await self.notification_client.react(ReactArgs(task_id, "📌"))
        # Remove tmp dir which contains all the images of the new task
        await self.dir_client.removedirs("tmp")
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return CreateTaskUseCaseOutput(
            content=self.task.name,
            description=f"[{self.task.category}]\n" + self.task.description,
            due_date=self.task.due_date,
            priority=self.task.priority,
        )
