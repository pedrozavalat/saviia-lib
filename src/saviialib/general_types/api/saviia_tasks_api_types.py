from dataclasses import dataclass

@dataclass
class SaviiaTasksConfig:
    notification_client_api_key: str

@dataclass 
class SaviiaTask:
    name: str
    description: str
    due_date: str
    priority: int
    assignee: str
    category: str
    images: list
    
    