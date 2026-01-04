from .types.create_task_types import CreateTaskUseCaseInput, CreateTaskUseCaseOutput
from saviialib.libs.log_client import LogClient, LogClientArgs, LogStatus, DebugArgs
from saviialib.libs.notification_client import NotifyArgs, ReactArgs
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.files_client import (
    FilesClient,
    FilesClientInitArgs,
    WriteArgs,
)


class CreateTaskUseCase:
    def __init__(self, input: CreateTaskUseCaseInput) -> None:
        self.task = input.task
        self.notification_client = input.notification_client
        self.log_client = LogClient(
            LogClientArgs(service_name="tasks", class_name="create_tasks")
        )
        self.dir_client = DirectoryClient(DirectoryClientArgs("os_client"))
        self.files_client = FilesClient(FilesClientInitArgs("aiofiles_client"))

    def _format_priority(self, priority: int):
        """Priority between 1 to 4"""
        priority_nl = ["Urgente 🔴", "Alta 🟠", "Media 🟡", "Baja 🟢"]
        return priority_nl[priority + 1]

    async def execute(self) -> CreateTaskUseCaseOutput:
        self.log_client.method_name = "execute"
        self.log_client.debug(DebugArgs(LogStatus.STARTED))
        # Preprocess task content
        content = (
            f"## {self.task.name}\n"
            f"> {self._format_priority(int(self.task.priority))}\t|\t{self.task.category}\n"
            f"* __Descripcion__: {self.task.description}\n"
            f"* __Fecha de realización__: {self.task.due_date}\n"
            f"* __Persona asignada__: {self.task.assignee}\n"
        )
        files = []
        embeds = []
        if self.task.images:
            await self.dir_client.makedirs("tmp")
            for image in self.task.images:
                await self.files_client.write(
                    WriteArgs(
                        file_name=f"{image.name}.jpeg",
                        file_content=image.data,
                        mode="jpeg",
                        destination_path="tmp",
                    )
                )
                files.append(f"./tmp/{image.name}.jpeg")
                embeds.append({"image": {"url": f"attachment://{image.name}.jpeg"}})
        # Create new task at #created-tasks in discorc
        async with self.notification_client:
            new_task = await self.notification_client.notify(
                NotifyArgs(content=content, embeds=embeds, files=files)
            )
        task_id = new_task["id"]
        # Mark as need to action
        async with self.notification_client:
            await self.notification_client.react(ReactArgs(task_id, "📌"))
        # Remove tmp dir which contains all the images of the new task
        await self.dir_client.removedirs("./tmp")
        self.log_client.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return CreateTaskUseCaseOutput(
            content=self.task.name,
            description=f"[{self.task.category}]\n" + self.task.description,
            due_date=self.task.due_date,
            priority=self.task.priority,
        )
