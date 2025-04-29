from .clients.sharepoint_rest_api import SharepointRestAPI
from .sharepoint_client_contract import SharepointClientContract
from .types.sharepoint_client_types import (
    SharepointClientInitArgs,
    SpListFilesArgs,
    SpListFoldersArgs,
    SpUploadFileArgs,
)


class SharepointClient(SharepointClientContract):
    CLIENTS = {"sharepoint_rest_api"}

    def __init__(self, args: SharepointClientInitArgs):
        if args.client_name not in SharepointClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)
        elif args.client_name == "sharepoint_rest_api":
            self.client_obj = SharepointRestAPI(args)

    async def __aenter__(self):
        return await self.client_obj.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client_obj.__aexit__(exc_type, exc_val, exc_tb)

    async def list_files(self, args: SpListFilesArgs) -> list:
        return await self.client_obj.list_files(args)

    async def list_folders(self, args: SpListFoldersArgs) -> list:
        return await self.client_obj.list_files(args)

    async def upload_file(self, args: SpUploadFileArgs) -> dict:
        return await self.client_obj.upload_file(args)
