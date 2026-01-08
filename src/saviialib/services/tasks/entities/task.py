from dataclasses import dataclass, field

@dataclass 
class SaviiaTask:
    name: str
    due_date: str
    priority: int
    description: str = ""
    assignee: str = ""
    category: str = ""
    images: list = field(default_factory=list)
    completed: bool = False
    
    