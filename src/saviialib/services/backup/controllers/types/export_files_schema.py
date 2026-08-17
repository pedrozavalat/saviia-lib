EXPORT_FILES_SCHEMA = {
    "title": "Controller input schema for exporting local backup files",
    "description": (
        "Schema for validating input data when exporting a local backup folder to SAVIIA Cloud provider."
    ),
    "type": "object",
    "properties": {
        "local_backup_path": {"type": "string"},
        "local_folder_path": {"type": "string"},
        "cloud_provider_destination_path": {"type": "string"},
    },
    "required": [
        "local_backup_path",
        "local_folder_path",
        "cloud_provider_destination_path",
    ],
    "additionalProperties": False,
}
