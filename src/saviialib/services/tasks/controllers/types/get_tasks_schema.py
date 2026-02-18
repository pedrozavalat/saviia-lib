GET_TASKS_SCHEMA = {
    "title": "Controller input schema for retrieving all tasks that have been created",
    "description": "Schema for validating input data when retrieving all the tasks created in Saviia",
    "type": "object",
    "properties": {
        "bot_token": {"type": "string"},
        "task_channel_id": {"type": "string"},
        "params": {
            "type": "object",
            "properties": {
                "sort": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                },
                "after": {"type": "integer"},
                "before": {"type": "integer"},
                "completed": {"type": "boolean"},
                "fields": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["title", "due_date", "priority", "description"],
                    },
                    "uniqueItems": True,
                    "allOf": [
                        {"contains": {"const": "title"}},
                        {"contains": {"const": "due_date"}},
                    ],
                    "description": "Specific fields to include in the response",
                },
            },
            "additionalProperties": False,
        },
    },
    "required": ["bot_token", "task_channel_id"],
    "additionalProperties": False,
}
