CREATE_TASK_SCHEMA = {
    "title": "Controller input schema for creating a task",
    "description": "Schema for validating input data when creating a task in Saviia",
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "minLength": 1,
        },
        "description": {"type": "string"},
        "deadline": {
            "type": "string",
            "format": "date-time",
            "minLength": 1,
        },
        "creation": {
            "type": "string",
            "format": "date-time",
            "minLength": 1,
        },
        "execution": {
            "type": "string",
            "format": "date-time",
        },
        "priority": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "minLength": 1,
        },
        "assignee": {
            "type": "string",
            "minLength": 1,
        },
        "assignee_email": {"type": "string", "format": "email"},
        "assignee_discord_username": {"type": "string"},
        "category": {"type": "string"},
        "periodicity": {"type": "string"},
        "bot_token": {"type": "string"},
        "task_channel_id": {"type": "string"},
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
        "bot_token",
        "task_channel_id",
        "title",
        "deadline",
        "creation",
        "priority",
        "assignee",
    ],
    "additionalProperties": False,
}
