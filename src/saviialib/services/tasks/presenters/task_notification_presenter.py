from saviialib.services.tasks.entities.task import SaviiaTask


class TaskNotificationPresenter:
    PRIORITY_LABELS = ["Urgente 🔴", "Alta 🟠", "Media 🟡", "Baja 🔵"]

    @classmethod
    def _format_priority(cls, priority: int) -> str:
        return cls.PRIORITY_LABELS[priority - 1]

    @classmethod
    def to_markdown(cls, task: SaviiaTask) -> str:
        return (
            f"## {task.name}\n"
            f"> {cls._format_priority(task.priority)}\t|\t{task.category}\n"
            f"* __Descripcion__: {task.description}\n"
            f"* __Fecha de realización__: {task.due_date}\n"
            f"* __Persona asignada__: {task.assignee}\n"
        )
