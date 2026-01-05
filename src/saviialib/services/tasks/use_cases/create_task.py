from .types.create_task_types import CreateTaskUseCaseInput, CreateTaskUseCaseOutput
from saviialib.libs.log_client import LogClient, LogClientArgs, LogStatus, DebugArgs
from saviialib.libs.notification_client import (
    NotifyArgs,
    ReactArgs,
    FindNotificationArgs,
)
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
        content = self.presenter.to_markdown(self.task)
        files = []
        embeds = []
        if self.task.images:
            await self.dir_client.makedirs("tmp")
            for image in self.task.images:
                await self.files_client.write(
                    WriteArgs(
                        file_name=f"{image['name']}",
                        file_content=image['data'],
                        mode="jpeg",
                        destination_path="tmp",
                    )
                )
                files.append(f"./tmp/{image['name']}")
                embeds.append({"image": {"url": f"attachment://{image['name']}"}})
        # Check if notification is already created at the discord channel
        
        exists = await self.notification_client.find_notification(
            FindNotificationArgs(content=self.task.name, reactions=["📌"])
        )
        if exists:
            self.log_client.debug(DebugArgs(LogStatus.ALERT))
            raise ExistingNotificationError(
                reason="A task with the same name already exists in the notification channel."
            )

        # Create new task at #created-tasks in discord
        new_task = await self.notification_client.notify(
            NotifyArgs(content=content, embeds=embeds, files=files)
        )
        task_id = new_task["id"]
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
