from saviialib.services.tasks.entities.task import SaviiaTask
from saviialib.libs.zero_dependency.utils.datetime_utils import (
    is_within_date_range,
    str_to_timestamp,
)


class TaskNotificationPresenter:
    PRIORITY_LABELS = ["Urgente 🔴", "Alta 🟠", "Media 🟡", "Baja 🔵"]

    @classmethod
    def _format_priority(cls, priority: int) -> str:
        return cls.PRIORITY_LABELS[priority - 1]

    @classmethod
    def _format_content(cls, content: str) -> dict[str, str]:
        return {
            "title": content.split("\n")[0].replace("#", "").strip(),
            "priority": content.split("\n")[1].split("|")[0].replace(">", "").strip(),
            "category": content.split("\n")[1].split("|")[1].strip(),
            "description": content.split("\n")[2].split(":")[1].strip(),
            "due_date": content.split("\n")[3].split(":")[1].strip(),
            "assignee": content.split("\n")[4].split(":")[1].strip(),
        }

    @classmethod
    def to_markdown(cls, task: SaviiaTask) -> str:
        return (
            f"## {task.name}\n"
            f"> {cls._format_priority(task.priority)}\t|\t{task.category}\n"
            f"* __Descripcion__: {task.description}\n"
            f"* __Fecha de realización__: {task.due_date}\n"
            f"* __Persona asignada__: {task.assignee}\n"
        )

    @classmethod
    def _format_complete_status(cls, reactions: list[dict]) -> bool:
        if any(reaction["emoji"]["name"] == "✅" for reaction in reactions):
            return True
        return False

    @classmethod
    def to_task_notifications(
        cls, tasks: list, params: dict = {}
    ) -> list[dict[str, str | bool | dict]]:
        tasks = list(
            map(
                lambda task: {
                    "task": cls._format_content(task["content"]),
                    "discord_id": task["id"],
                    "completed": cls._format_complete_status(task["reactions"]),
                },
                filter(
                    lambda task: task.get("reactions", {}) != {}
                    and (
                        {"📌", "✅"}
                        & {r["emoji"]["name"] for r in task.get("reactions")}
                        != {}
                    ),
                    tasks,
                ),
            )
        )

        if params.get("completed"):
            tasks = list(filter(lambda t: t["completed"] == params["completed"], tasks))

        if params.get("fields"):
            allowed_fields = params["fields"]
            tasks = list(
                map(
                    lambda t: {
                        "task": {
                            k: v for k, v in t["task"].items() if k in allowed_fields
                        },
                        "discord_id": t["discord_id"],
                        "completed": t["completed"],
                    },
                    tasks,
                )
            )

        if params.get("after") or params.get("before"):
            tasks = list(
                map(
                    lambda t: is_within_date_range(
                        t["task"]["due_date"], params.get("after"), params.get("before")
                    ),
                    tasks,
                )
            )
        if params.get("sort"):
            reverse = params["sort"] == "desc"
            tasks.sort(
                key=lambda t: str_to_timestamp(
                    t["task"]["due_date"], date_format="%Y-%m-%d"
                ),
                reverse=reverse,
            )
        return tasks
