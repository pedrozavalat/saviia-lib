from dataclasses import dataclass, field


@dataclass
class SaviiaTask:
    """Task entity representing a user's task with scheduling and metadata.

    Attributes:
        tid: Task ID
        title: Task title
        deadline: Deadline date for the task. The user should have completed the task by this date.
        creation: Creation date of the task. 
        execution: The date on which the user indicated the task had been completed.
        priority: Task priority level
        description: Optional task details
        periodicity: Recurrence pattern (e.g., "every 2 weeks")
        assignee: Person assigned to the task
        assignee_email: Email of the person assigned to the task
        assignee_discord_username: Discord username of the person assigneg to the task
        category: Task category/classification
        completed: Whether the task is completed
        images: list of dictionaries containing information about Base64 images loaded from the frontend.
    """

    title: str
    deadline: str
    creation: str
    priority: int
    assignee: str
    completed: bool
    execution: str = ""
    assignee_email: str = ""
    assignee_discord_username: str = ""
    tid: str = ""
    description: str = ""
    periodicity: str = ""
    category: str = ""
    images: list = field(default_factory=list)
