from dataclasses import dataclass
from logging import Logger
from typing import Literal


@dataclass
class SaviiaBackupConfig:
    """
    Configuration for backing up files to a cloud provider.

    Attributes:
        client_name (Literal["sharepoint_rest_api", "databricks"]): Target cloud provider.
        local_backup_path (str): Local path to backup.
        sharepoint_*: SharePoint credentials (required only for SharePoint client).
        databricks_*: Databricks credentials (required only for Databricks client).
    """

    logger: Logger
    local_backup_path: str
    client_name: Literal["sharepoint_rest_api", "databricks"] = "databricks"

    # SharePoint (required only when client_name == "sharepoint_rest_api")
    sharepoint_client_id: str | None = None
    sharepoint_client_secret: str | None = None
    sharepoint_tenant_id: str | None = None
    sharepoint_tenant_name: str | None = None
    sharepoint_site_name: str | None = None

    # Databricks (required only when client_name == "databricks")
    databricks_api_key: str | None = None
    databricks_host_url: str | None = None
