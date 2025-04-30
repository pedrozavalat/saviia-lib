from dataclasses import dataclass


@dataclass
class EpiiUpdateThiesConfig:
    """
    Configuration for Epii API.

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
        logger (Logger): Logger object for logging during synchronisation of files from THIES Data Logger
    """

    ftp_port: int
    ftp_host: str
    ftp_user: str
    ftp_password: str
    sharepoint_client_id: str
    sharepoint_client_secret: str
    sharepoint_tenant_id: str
    sharepoint_tenant_name: str
    sharepoint_site_name: str
