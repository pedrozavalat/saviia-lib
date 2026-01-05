GET_TASKS_SCHEMA = {
    "title": "Controller input schema for retrieving all tasks that have been created",
    "description": "Schema for validating input data when retrieving all the tasks created in Saviia",
    "type": "object",
    "properties": {
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
    "required": ["config", "channel_id"],
    "additionalProperties": False,
}
