CREATE_TASK_SCHEMA = {
    "title": "Controller input schema for creating a task",
    "description": "Schema for validating input data when creating a task in Saviia",
    "type": "object",
    "properties": {
        "task": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "due_date": {
                    "type": "string",
                    "format": "date-time",
                },
                "priority": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 4,
                },
                "assignee": {"type": "string"},
                "category": {"type": "string"},
                "images": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "data": {"type": "string"},
                        },
                        "required": ["name", "type", "data"],
                        "additionalProperties": False,
                    },
                    "maxItems": 10,
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
            "additionalProperties": False,
        },
        "config": {
            "type": "object",
            "properties": {
                "notification_client_api_key": {"type": "string"},
            },
            "required": ["notification_client_api_key"],
            "additionalProperties": False,
        },
        "channel_id": {
            "type": "string",
        },
    },
    "required": ["task", "config", "channel_id"],
    "additionalProperties": False,
}
