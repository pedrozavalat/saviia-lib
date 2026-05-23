from dataclasses import dataclass
from logging import Logger


@dataclass
class SaviiaThiesConfig:
    """
    Configuration for Saviia Thies.

    Attributes:
        sharepoint_client_id (str): Client ID for SharePoint authentication.
        sharepoint_client_secret (str): Client secret for SharePoint authentication.
        sharepoint_tenant_id (str): Tenant ID for SharePoint authentication.
        sharepoint_tenant_name (str): Tenant name for SharePoint.
        sharepoint_site_name (str): Site name in SharePoint.
        latitude (str): Latitude at which the station is located (optional).
        longitude (str): Longitude at which the station is located (optional).
    """
    sharepoint_client_id: str
    sharepoint_client_secret: str
    sharepoint_tenant_id: str
    sharepoint_tenant_name: str
    sharepoint_site_name: str
    local_backup_path: str
    logger: Logger
    latitude: float = -91
    longitude: float = -181
    
