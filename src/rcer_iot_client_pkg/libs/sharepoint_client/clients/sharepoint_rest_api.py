import os
from typing import Any

from aiohttp import ClientError, ClientSession
from dotenv import load_dotenv

from rcer_iot_client_pkg.libs.sharepoint_client.sharepoint_client_contract import (
    SharepointClientContract,
)
from rcer_iot_client_pkg.libs.sharepoint_client.types.sharepoint_client_types import (
    SpListFilesArgs,
    SpListFoldersArgs,
    SpUploadFileArgs,
)

load_dotenv()


class SharepointRestAPI(SharepointClientContract):
    def __init__(self):
        self.session: ClientSession | None = None
        self.base_headers = {}
        self.credentials = {}
        self.base_url = ""

    async def _load_form_digest_value(self) -> str:
        try:
            response = await self.session.post("contextinfo")
            response_json = await response.json()
            return response_json["FormDigestValue"]
        except ClientError as error:
            raise ConnectionError(error) from error

    async def _load_credentials(self) -> dict:
        tenant_id = os.getenv("TENANT_ID")
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        resource_base = "00000003-0000-0ff1-ce00-000000000000"
        resource = (
            f"{resource_base}/{os.getenv('TENANT_NAME')}.sharepoint.com@{tenant_id}"
        )
        url = f"https://accounts.accesscontrol.windows.net/{tenant_id}/tokens/OAuth/2"
        payload = {
            "grant_type": "client_credentials",
            "client_id": f"{client_id}@{tenant_id}",
            "client_secret": client_secret,
            "resource": resource,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        async with ClientSession() as session:
            # Load access token
            response = await session.post(url, data=payload, headers=headers)
            if response.status != 200:
                raise ClientError(
                    f"Failed to fetch credentials: {response.status}, {await response.text()}"
                )
            response_json = await response.json()

            return {
                "access_token": response_json["access_token"],
            }

    async def __aenter__(self) -> "SharepointRestAPI":
        self.credentials = await self._load_credentials()
        site_url = f"https://{os.getenv('TENANT_NAME')}.sharepoint.com"
        site_name = os.getenv("SITE_NAME")

        self.base_headers = {
            "Authorization": f"Bearer {self.credentials['access_token']}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.base_url = f"{site_url}/sites/{site_name}/_api/"
        self.session = ClientSession(headers=self.base_headers, base_url=self.base_url)
        return self

    async def __aexit__(
        self, _exc_type: type[BaseException], _exc_val: BaseException, _exc_tb: Any
    ) -> None:
        await self.session.close()

    async def list_files(self, args: SpListFilesArgs) -> list:
        try:
            folder_relative_url = (
                f"GetFolderByServerRelativeUrl('{args.folder_relative_url}')"
            )
            endpoint = f"web/{folder_relative_url}/Files"
            response = await self.session.get(endpoint.lstrip("/"))
            response.raise_for_status()
            response_json = await response.json()
            return response_json
        except ClientError as error:
            raise ConnectionError(error) from error

    async def list_folders(self, args: SpListFoldersArgs) -> list:
        try:
            folder_relative_url = (
                f"GetFolderByServerRelativeUrl('{args.folder_relative_url}')"
            )
            endpoint = f"web/{folder_relative_url}/Folder"
            response = await self.session.get(endpoint.lstrip("/"))
            response.raise_for_status()
            return await response.json()
        except ClientError as error:
            raise ConnectionError(error) from error

    async def upload_file(self, args: SpUploadFileArgs) -> dict:
        try:
            # Load form digest value
            form_digest_value = await self._load_form_digest_value()
            headers = {
                **self.base_headers,
                "X-RequestDigest": form_digest_value,
                "Content-Type": "application/octet-stream",
            }
            # Upload the file in the requested folder
            folder_relative_url = (
                f"GetFolderByServerRelativeUrl('{args.folder_relative_url}')"
            )
            # Read the file
            source_file_path = os.path.basename(args.file_path)
            with open(source_file_path, "rb") as file:
                data = file.read()

            endpoint = f"web/{folder_relative_url}/Files/add(url='{source_file_path}',overwrite=false)"
            response = await self.session.post(endpoint, data=data, headers=headers)

            response.raise_for_status()
            return await response.json()
        except ClientError as error:
            raise ConnectionError(error) from error
