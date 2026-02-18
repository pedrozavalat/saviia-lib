from .types.create_task_types import CreateTaskUseCaseInput, CreateTaskUseCaseOutput
from saviialib.libs.log_client import LogClient, LogClientArgs, LogStatus, DebugArgs
from saviialib.libs.notification_client import (
    NotifyArgs,
    ReactArgs,
)
from saviialib.services.tasks.presenters import TaskNotificationPresenter
from saviialib.libs.files_client import (
    FilesClient,
    FilesClientInitArgs,
    WriteArgs,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs


class CreateTaskUseCase:
    def __init__(self, input: CreateTaskUseCaseInput) -> None:
        self.logger = LogClient(
            LogClientArgs(service_name="tasks", class_name="delete_task")
        )
        self.dir_client = DirectoryClient(DirectoryClientArgs("os_client"))
        self.files_client = FilesClient(FilesClientInitArgs("aiofiles_client"))
        self.task = input.task
        self.notification_client = input.notification_client
        self.presenter = TaskNotificationPresenter()

    async def execute(self) -> CreateTaskUseCaseOutput:
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        # Preprocess the task content
        content = self.presenter.to_markdown(self.task.__dict__)
        files, embeds = [], []
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
        # Upload the taks to Discord
        new_task = await self.notification_client.notify(
            NotifyArgs(content=content, embeds=embeds, files=files)
        )
        await self.notification_client.react(ReactArgs(new_task["id"], "📌"))
        # Remove the tmp dir
        await self.dir_client.removedirs("tmp")
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return CreateTaskUseCaseOutput(task_id=new_task["id"])
