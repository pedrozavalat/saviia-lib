DELETE_TASK_SCHEMA = {
    "title": "Controller input schema for deleting a task",
    "description": "Schema for validating input data when deleting a task in Saviia",
    "type": "object",
    "properties": {
        "task_id": {"type": "string"},
        "webhook_url": {"type": "string"},
        "channel_id": {"type": "string"},
    },
    "required": [
        "webhook_url",
        "task_id",
    ],
    "additionalProperties": False,
}
