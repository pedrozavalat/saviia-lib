DELETE_TASK_SCHEMA = {
    "title": "Controller input schema for deleting a task",
    "description": "Schema for validating input data when deleting a task in Saviia",
    "type": "object",
    "properties": {
        "task_id": {"type": "string"},
        "bot_token": {"type": "string"},
        "task_channel_id": {"type": "string"},
    },
    "required": ["bot_token", "task_id", "task_channel_id"],
    "additionalProperties": False,
}
