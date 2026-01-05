from dataclasses import dataclass

@dataclass 
class SaviiaTask:
    name: str
    description: str
    due_date: str
    priority: int
    assignee: str
    category: str
    images: list
    completed: bool = False
    
    