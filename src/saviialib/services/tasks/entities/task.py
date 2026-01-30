from dataclasses import dataclass

@dataclass 
class SaviiaTask:
    tid: str # Task ID
    title: str
    deadline: str
    priority: int
    description: str 
    periodicity: str
    assignee: str
    category: str 
    completed: bool

    
    