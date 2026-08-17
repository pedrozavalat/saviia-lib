GET_THIES_DATA_SCHEMA = {
    "title": "Controller input schema for retrieving THIES data",
    "description": "Schema for validating input data when getting THIES synchronization status.",
    "type": "object",
    "properties": {
        "local_backup_path": {"type": "string"},
        "cloud_provider_destination_path": {"type": "string"},
        "ftp_host": {"type": "string"},
        "ftp_port": {"type": "integer"},
        "ftp_user": {"type": "string"},
        "ftp_password": {"type": "string"},
    },
    "required": [
        "local_backup_path",
        "cloud_provider_destination_path",
        "ftp_host",
        "ftp_port",
        "ftp_user",
        "ftp_password",
    ],
    "additionalProperties": False,
}
