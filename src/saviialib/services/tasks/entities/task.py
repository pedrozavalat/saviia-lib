from dataclasses import dataclass, field


@dataclass
class SaviiaTask:
    """Task entity representing a user's task with scheduling and metadata.

    Attributes:
        tid: Task ID
        title: Task title
        deadline: Completion date for the task
        priority: Task priority level
        description: Optional task details
        periodicity: Recurrence pattern (e.g., "every 2 weeks")
        assignee: Person assigned to the task
        category: Task category/classification
        completed: Whether the task is completed
        images: list of dictionaries containing information about Base64 images loaded from the frontend.
    """

    title: str
    deadline: str
    priority: int
    assignee: str
    completed: bool
    tid: str = ""
    description: str = ""
    periodicity: str = ""
    category: str = ""
    images: list = field(default_factory=list)
