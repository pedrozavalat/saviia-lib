DETECT_FAILURES_SCHEMA = {
    "title": "Controller input schema for Detect Failures in THIES sensors",
    "description": "Schema for controller input to detect failures in THIES data retrieval.",
    "type": "object",
    "properties": {
        "local_backup_source_path": {"type": "string"},
        "db_driver": {"type": "string"},
        "db_host": {"type": "string"},
        "db_name": {"type": "string"},
        "user": {"type": "string"},
        "pwd": {"type": "string"},
        "n_days": {"type": "integer"},
    },
    "required": [
        "local_backup_source_path",
        "n_days",
    ],
    "additionalProperties": False,
}
