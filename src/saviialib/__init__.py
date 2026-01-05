# read version from installed package
from importlib.metadata import version

__version__ = version("saviialib")

from .general_types.api.saviia_api_types import SaviiaAPIConfig

from typing import Dict, Type, Any, overload, Literal, List

from saviialib.services import (
    SaviiaThiesConfig,
    SaviiaThiesAPI,
    SaviiaBackupAPI,
    SaviiaBackupConfig,
    SaviiaTasksAPI,
    SaviiaTasksConfig,
)

__all__ = ["SaviiaAPI", "SaviiaAPIConfig"]


class SaviiaAPI:
    API_REGISTRY: Dict[str, Type] = {
        "thies": SaviiaThiesAPI,
        "backup": SaviiaBackupAPI,
        "tasks": SaviiaTasksAPI,
    }

    @overload
    def get(self, name: Literal["thies"]) -> SaviiaThiesAPI: ...
    @overload
    def get(self, name: Literal["backup"]) -> SaviiaBackupAPI: ...
    @overload
    def get(self, name: Literal["tasks"]) -> SaviiaTasksAPI: ...

    def __init__(self, config: SaviiaAPIConfig):
        """
        Receive a dictionary of configurations, with the same key
        as those registered in API_REGISTRY.

        :params configs: Dictionary of configurations for each API.

        Example:
            configs = {
                "thies": SaviiaThiesConfig(...),
                "backup": SaviiaBackupConfig(...),
                "tasks": SaviiaTasksConfig(...),
            }
        """
        self._instances: Dict[str, Any] = {}

        for name, api_class in SaviiaAPI.API_REGISTRY.items():
            if name == "thies":
                service_config = SaviiaThiesConfig(
                    ftp_host=config.ftp_host,
                    ftp_port=config.ftp_port,
                    ftp_user=config.ftp_user,
                    ftp_password=config.ftp_password,
                    sharepoint_client_id=config.sharepoint_client_id,
                    sharepoint_client_secret=config.sharepoint_client_secret,
                    sharepoint_tenant_id=config.sharepoint_tenant_id,
                    sharepoint_tenant_name=config.sharepoint_tenant_name,
                    sharepoint_site_name=config.sharepoint_site_name,
                    logger=config.logger,
                )
            elif name == "backup":
                service_config = SaviiaBackupConfig(
                    sharepoint_client_id=config.sharepoint_client_id,
                    sharepoint_client_secret=config.sharepoint_client_secret,
                    sharepoint_tenant_id=config.sharepoint_tenant_id,
                    sharepoint_tenant_name=config.sharepoint_tenant_name,
                    sharepoint_site_name=config.sharepoint_site_name,
                    logger=config.logger,
                )
            elif name == "tasks":
                service_config = SaviiaTasksConfig(
                    notification_client_api_key=config.notification_client_api_key, 
                )

            self._instances[name] = api_class(service_config)

    def get(self, name: Literal["thies", "backup", "tasks"]) -> Any:
        """Returns the API instance associated with the given name."""
        try:
            return self._instances[name]
        except KeyError:
            raise ValueError(f"API '{name}' is not registered or not configured.")

    def list_available(self) -> List[str]:
        """List of available registered APIs."""
        return list(self._instances.keys())
