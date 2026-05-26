EXPORT_FILES_SCHEMA = {
    "title": "Controller input schema for exporting local backup files",
    "description": (
        "Schema for validating input data when exporting a local backup folder to SharePoint."
    ),
    "type": "object",
    "properties": {
        "sharepoint_client_id": {"type": "string"},
        "sharepoint_client_secret": {"type": "string"},
        "sharepoint_tenant_id": {"type": "string"},
        "sharepoint_tenant_name": {"type": "string"},
        "sharepoint_site_name": {"type": "string"},
        "local_backup_path": {"type": "string"},
        "local_folder_path": {"type": "string"},
        "sharepoint_destination_path": {"type": "string"},
    },
    "required": [
        "sharepoint_client_id",
        "sharepoint_client_secret",
        "sharepoint_tenant_id",
        "sharepoint_tenant_name",
        "sharepoint_site_name",
        "local_backup_path",
        "local_folder_path",
        "sharepoint_destination_path",
    ],
    "additionalProperties": False,
}
