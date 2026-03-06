GET_PENDING_TASKS_SCHEMA = {
    "title": "Controller input schema for retrieving all the tasks that are still unfinished",
    "description": "Schema for validating input data when retrieving all the tasks that are still unfinished in SAVIIA",
    "type": "object",
    "properties": {
        "bot_token": {"type": "string"},
        "task_channel_id": {"type": "string"},
    },
    "required": ["bot_token", "task_channel_id"],
    "additionalProperties": False,
}
