from .clients.sharepoint_rest_api import SharepointRestAPI
from .clients.databricks import DatabricksClient

from .cloud_client_contract import CloudClientContract
from .types.cloud_client_types import (
    CloudClientInitArgs,
    CloudClientListFilesArgs,
    CloudClientListFoldersArgs,
    CloudClientUploadFileArgs,
    CloudClientCreateFolderArgs,
    CloudClientResolveUrlArgs
)


class CloudClient(CloudClientContract):
    CLIENTS = {"sharepoint_rest_api", "databricks"}

    def __init__(self, args: CloudClientInitArgs):
        if args.client_name not in self.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)
        elif args.client_name == "sharepoint_rest_api":
            self.client_obj = SharepointRestAPI(args)
        elif args.client_name == "databricks":
            self.client_obj = DatabricksClient(args)

    @property
    def base_url(self):
        return self.client_obj.base_url
    
    @property
    def tenant_id(self):
        return getattr(self.client_obj, "tenant_id", None)

    @property
    def tenant_name(self):
        return getattr(self.client_obj, "tenant_name", None)

    @property
    def site_name(self):
        return getattr(self.client_obj, "site_name", None)

    @property
    def client_id(self):
        return getattr(self.client_obj, "client_id", None)

    @property
    def client_secret(self):
        return getattr(self.client_obj, "client_secret", None)

    @property
    def api_key(self):
        return getattr(self.client_obj, "api_key", None)

    @property
    def host_url(self):
        return getattr(self.client_obj, "host_url", None)

    async def __aenter__(self):
        return await self.client_obj.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client_obj.__aexit__(exc_type, exc_val, exc_tb)

    async def list_files(self, args: CloudClientListFilesArgs) -> list:
        return await self.client_obj.list_files(args)

    async def list_folders(self, args: CloudClientListFoldersArgs) -> list:
        return await self.client_obj.list_folders(args)

    async def upload_file(self, args: CloudClientUploadFileArgs) -> dict:
        return await self.client_obj.upload_file(args)

    async def create_folder(self, args: CloudClientCreateFolderArgs) -> dict:
        return await self.client_obj.create_folder(args)
    
    def resolve_url(self, args: CloudClientResolveUrlArgs) -> str:
        return self.client_obj.resolve_url(args)
