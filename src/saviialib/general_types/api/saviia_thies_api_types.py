from dataclasses import dataclass
from logging import Logger
from typing import Literal


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
        local_backup_path (str): Path for local backup storage.
        logger (Logger): Logger instance for logging.
        databricks_api_key (str): API key for Databricks authentication (optional).
        databricks_host_url (str): Host URL for Databricks (optional).
        latitude (str): Latitude at which the station is located (optional).
        longitude (str): Longitude at which the station is located (optional).
    """

    local_backup_path: str
    logger: Logger
    cloud_client_name: Literal["sharepoint_rest_api", "databricks"] 
    sharepoint_client_id: str = ""
    sharepoint_client_secret: str = ""
    sharepoint_tenant_id: str = ""
    sharepoint_tenant_name: str = ""
    sharepoint_site_name: str = ""
    databricks_api_key: str = ""
    databricks_host_url: str = ""
    latitude: float = -91
    longitude: float = -181
