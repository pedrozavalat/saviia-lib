from dataclasses import dataclass
from logging import Logger


@dataclass
class SaviiaBackupConfig:
    """
    Configuration for backing up files to SharePoint.

    Attributes:
        sharepoint_client_id (str): Client ID for SharePoint authentication.
        sharepoint_client_secret (str): Client secret for SharePoint authentication.
        sharepoint_tenant_id (str): Tenant ID for SharePoint authentication.
        sharepoint_tenant_name (str): Tenant name for SharePoint.
        sharepoint_site_name (str): Site name in SharePoint.
        local_backup_source_path (str): Local path to backup.
    """

    sharepoint_client_id: str
    sharepoint_client_secret: str
    sharepoint_tenant_id: str
    sharepoint_tenant_name: str
    sharepoint_site_name: str
    logger: Logger
