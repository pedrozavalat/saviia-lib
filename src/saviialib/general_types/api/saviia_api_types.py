from dataclasses import dataclass
from logging import Logger


@dataclass
class SaviiaAPIConfig:
    """
    Configuration for SAVIIA API.

    Attributes:
        ftp_port (int): Port number of the FTP server.
        ftp_host (str): Hostname or IP address of the FTP server.
        ftp_user (str): Username for the FTP server.
        ftp_password (str): Password for the FTP server.
        sharepoint_client_id (str): Client ID for SharePoint authentication.
        sharepoint_client_secret (str): Client secret for SharePoint authentication.
        sharepoint_tenant_id (str): Tenant ID for SharePoint authentication.
        sharepoint_tenant_name (str): Tenant name for SharePoint.
        sharepoint_site_name (str): Site name in SharePoint.
        databricks_api_key (str): API Key for Databricks.
        databricks_host_url (str): Host URL for Databricks.
        notification_client_api_key (str): API Key for Notification Client (Discord)
    """

    logger: Logger
    local_backup_path: str
    latitude: float = -91
    longitude: float = -181
    tasks_channel_id: str = ""
    bot_token: str = ""
    email_address: str = ""
    email_password: str = ""
    # SharePoint 
    sharepoint_client_id: str | None = None
    sharepoint_client_secret: str | None = None
    sharepoint_tenant_id: str | None = None
    sharepoint_tenant_name: str | None = None
    sharepoint_site_name: str | None = None

    # Databricks 
    databricks_api_key: str = ""
    databricks_host_url: str = ""


@dataclass
class FtpClientConfig:
    ftp_host: str
    ftp_port: int
    ftp_user: str
    ftp_password: str


@dataclass
class SharepointConfig:
    sharepoint_client_id: str
    sharepoint_client_secret: str
    sharepoint_tenant_id: str
    sharepoint_tenant_name: str
    sharepoint_site_name: str

@dataclass
class DatabricksConfig:
    databricks_api_key: str
    databricks_host_url: str