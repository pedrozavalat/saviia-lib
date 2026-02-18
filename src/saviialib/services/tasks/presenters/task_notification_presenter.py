from saviialib.libs.zero_dependency.utils.datetime_utils import (
    is_within_date_range,
    str_to_timestamp,
)


class TaskNotificationPresenter:
    @classmethod
    def to_dict(cls, content: str) -> dict[str, str]:
        lines = [line.strip() for line in content.strip().split("\n") if line.strip()]
        result = {}
        result["title"] = lines[0].lstrip("#").strip()
        for line in lines[2:]:
            if "__Estado__" in line:
                status = line.split(":")[1].strip()
                result["completed"] = False if "Pendiente" in status else True
            elif "__Fecha de realización__" in line:
                result["deadline"] = line.split(":")[1].strip()
            elif "__Descripcion__" in line:
                result["description"] = line.split(":")[1].strip()
            elif "__Periodicidad__" in line:
                result["periodicity"] = line.split(":")[1].strip()
            elif "__Prioridad__" in line:
                result["priority"] = line.split(":")[1].strip()
            elif "__Categoría__" in line:
                result["category"] = line.split(":")[1].strip()
            elif "__Persona asignada__" in line:
                result["assignee"] = line.split(":")[1].strip()
        return result

    @classmethod
    def to_markdown(cls, task: dict[str, str]) -> str:
        status = "Completada" if task.get("completed") else "Pendiente"
        markdown = f"## {task.get('title')}\n"
        markdown += f"* __Estado__: {status}\n"
        markdown += f"* __Fecha de realización__: {task.get('deadline')}\n"
        markdown += f"* __Prioridad__: {task.get('priority')}\n"
        if task.get("description"):
            markdown += f"* __Descripcion__: {task.get('description')}\n"
        if task.get("periodicity"):
            markdown += f"* __Periodicidad__: {task.get('periodicity')}\n"
        if task.get("assignee"):
            markdown += f"* __Persona asignada__: {task.get('assignee')}\n"
        if task.get("category"):
            markdown += f"* __Categoría__: {task.get('category')}\n"
        return markdown

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
                    **cls.to_dict(task["content"]),
                    "task_id": task["id"],
                    "embeds": list(map(lambda e: e["image"]["url"], task["embeds"])),
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
