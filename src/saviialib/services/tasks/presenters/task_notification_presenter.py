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
            elif "__Fecha limite__" in line:
                result["deadline"] = line.split(":")[1].strip()
            elif "__Fecha creación__" in line:
                result["creation"] = line.split(":")[1].strip()
            elif "__Fecha de ejecución__" in line:
                result["execution"] = line.split(":")[1].strip()
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
            elif "__Email de la persona asignada__" in line:
                result["assignee_email"] = line.split(":")[1].strip()
            elif "__Discord username de la persona asignada__" in line:
                result["assignee_discord_username"] = line.split(":")[1].strip()
        return result

    @classmethod
    def to_markdown(cls, task: dict[str, str]) -> str:
        status = "Completada" if task.get("completed") else "Pendiente"
        markdown = f"## {task.get('title')}\n"
        markdown += f"__Estado__: {status}\n"
        markdown += f"__Fecha limite__: {task.get('deadline')}\n"
        markdown += f"__Fecha creación__: {task.get('creation')}\n"
        markdown += f"__Prioridad__: {task.get('priority')}\n"
        if task.get("description"):
            markdown += f"__Descripcion__: {task.get('description')}\n"
        if task.get("periodicity"):
            markdown += f"__Periodicidad__: {task.get('periodicity')}\n"
        if task.get("assignee"):
            markdown += f"__Persona asignada__: {task.get('assignee')}\n"
        if task.get("category"):
            markdown += f"__Categoría__: {task.get('category')}\n"
        if task.get("assignee_email"):
            markdown += (
                f"__Email de la persona asignada__: {task.get('assignee_email')}\n"
            )
        if task.get("assignee_discord_username"):
            markdown += f"__Discord username de la persona asignada__: {task.get('assignee_discord_username')}\n"
        if task.get("execution"):
            markdown += f"__Fecha de ejecución__: {task.get('execution')}\n"
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

        if any(param == "completed" for param in params.keys()):
            tasks = list(filter(lambda t: t["completed"] == params["completed"], tasks))

        if any(param == "fields" for param in params.keys()):
            allowed_fields = params["fields"]
            tasks = list(
                map(
                    lambda t: {k: v for k, v in t.items() if k in allowed_fields},
                    tasks,
                )
            )

        if any(param == "after" or param == "before" for param in params.keys()):
            tasks = list(
                map(
                    lambda t: is_within_date_range(
                        t["task"]["due_date"], params.get("after"), params.get("before")
                    ),
                    tasks,
                )
            )
        if any(param == "sort" for param in params.keys()):
            reverse = params["sort"] == "desc"
            tasks.sort(
                key=lambda t: str_to_timestamp(
                    t["task"]["due_date"], date_format="%Y-%m-%d"
                ),
                reverse=reverse,
            )
        return tasks
