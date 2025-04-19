import asyncio

from .clients.sharepoint_rest_api import SharepointRestAPI
from .sharepoint_client_contract import SharepointClientContract
from .types.sharepoint_client_types import (
    ListFilesArgs,
    SharepointClientInitArgs,
    UploadFileArgs,
)


class SharepointClient(SharepointClientContract):
    CLIENTS = {"sharepoint_rest_api"}

    def __init__(self, args: SharepointClientInitArgs):
        if args.client_name not in SharepointClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)
        elif args.client_name == "sharepoint_rest_api":
            self.client_obj = SharepointRestAPI()

    async def list_files(self, args: ListFilesArgs) -> list:
        return self.client_obj.list_files(args)

    async def list_folders(self, args: ListFilesArgs) -> list:
        return self.client_obj.list_files(args)

    async def upload_file(self, args: UploadFileArgs) -> dict:
        return self.client_obj.upload_file(args)


if __name__ == "__main__":
    api = SharepointClient(SharepointClientInitArgs(client_name="sharepoint_rest_api"))
    files = []

    async def main():
        BASE_URL = "/sites/uc365_CentrosyEstacionesRegionalesUC/Shared Documents/General/Test_Raspberry/THIES"
        for folder in ["EXT", "AVG"]:
            url = f"{BASE_URL}/{folder}"
            args = ListFilesArgs(folder_relative_url=url)
            files = await api.list_files(args)
            print([(x["Name"], x["Length"]) for x in files["value"]])
        args = UploadFileArgs(
            file_path="20240528.BIN",
            folder_relative_url="{BASE_URL}/TEST",
        )
        form_response = await api.upload_file(args)
        print(form_response)

    asyncio.run(main())
