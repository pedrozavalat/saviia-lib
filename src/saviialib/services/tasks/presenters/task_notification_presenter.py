from saviialib.services.tasks.entities.task import SaviiaTask
from saviialib.libs.zero_dependency.utils.datetime_utils import (
    is_within_date_range,
    str_to_timestamp,
)


class TaskNotificationPresenter:
    @classmethod
    def to_dict(cls, content: str) -> dict[str, str]:
        lines = [line.strip() for line in content.strip().split("\n") if line.strip()]
        result = {}
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
