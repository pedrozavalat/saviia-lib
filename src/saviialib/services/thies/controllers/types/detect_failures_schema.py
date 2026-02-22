DETECT_FAILURES_SCHEMA = {
    "title": "Controller input schema for Detect Failures in THIES sensors",
    "description": "Schema for controller input to detect failures in THIES data retrieval.",
    "type": "object",
    "properties": {
        "db_driver": {"type": "string"},
        "db_host": {"type": "string"},
        "db_name": {"type": "string"},
        "user": {"type": "string"},
        "pwd": {"type": "string"},
    },
    "required": [
        "local_backup_source_path",
        "db_driver",
        "db_host",
        "db_name",
        "user",
        "pwd",
    ],
    "additionalProperties": False,
}
