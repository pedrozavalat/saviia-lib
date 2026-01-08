UPDATE_TASK_SCHEMA = {
    "title": "Controller input schema for updating a task",
    "description": "Schema for validating input data when updating a task in Saviia",
    "type": "object",
    "properties": {
        "config": {
            "type": "object",
            "properties": {
                "notification_client_api_key": {"type": "string"},
                "calendar_client_api_key": {"type": "string"},
            },
            "required": ["notification_client_api_key"],
            "additionalProperties": False,
        },
        "channel_id": {
            "type": "string",
        },
    },
    "required": ["config", "channel_id"],
    "additionalProperties": False,
}
