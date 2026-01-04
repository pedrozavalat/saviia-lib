CreateTaskSchema = {
    "title": "Task",
    "description": "A task object for creating tasks in Saviia",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name of the task",
        },
        "description": {
            "type": "string",
            "description": "A detailed description of the task",
        },
        "due_date": {
            "type": "string",
            "format": "date-time",
            "description": "The due date of the task in ISO 8601 format",
        },
        "priority": {
            "type": "integer",
            "description": "The priority level of the task (e.g., 1-4)",
        },
        "assignee": {
            "type": "string",
            "description": "The user assigned to the task",
        },
        "category": {
            "type": "string",
            "description": "The category of the task",
        },
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the image file",
                    },
                    "type": {
                        "type": "string",
                        "description": "The MIME type of the image file",
                    },
                    "data": {
                        "type": "string",
                        "description": "The base64-encoded data of the image file",
                    },
                },
            },
        },
        "required": [
            "name",
            "description",
            "due_date",
            "priority",
            "assignee",
            "category",
            
        ],
    },
}
