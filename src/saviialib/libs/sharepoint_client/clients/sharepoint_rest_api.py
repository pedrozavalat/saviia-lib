from typing import Any
import json
from aiohttp import ClientError, ClientSession, TCPConnector
from dotenv import load_dotenv
import ssl
import certifi

from saviialib.libs.sharepoint_client.sharepoint_client_contract import (
    SharepointClientContract,
)
from saviialib.libs.sharepoint_client.types.sharepoint_client_types import (
    SpListFilesArgs,
    SpListFoldersArgs,
    SpUploadFileArgs,
    SpCreateFolderArgs,
    SharepointClientInitArgs,
)

load_dotenv()
ssl_context = ssl.create_default_context(cafile=certifi.where())


class SharepointRestAPI(SharepointClientContract):
    def __init__(self, args: SharepointClientInitArgs):
        self.session: ClientSession | None = None
        self.base_headers = {}
        self.credentials = {}
        self.base_url = ""
        self.tenant_id = args.config.sharepoint_tenant_id
        self.tenant_name = args.config.sharepoint_tenant_name
        self.client_secret = args.config.sharepoint_client_secret
        self.client_id = args.config.sharepoint_client_id
        self.site_name = args.config.sharepoint_site_name

    async def _load_form_digest_value(self) -> str:
        try:
            response = await self.session.post("contextinfo")
            response_json = await response.json()
            return response_json["FormDigestValue"]
        except ClientError as error:
            raise ConnectionError(error) from error

    async def _load_credentials(self) -> dict:
        resource_base = "00000003-0000-0ff1-ce00-000000000000"
        resource = f"{resource_base}/{self.tenant_name}.sharepoint.com@{self.tenant_id}"
        url = f"https://accounts.accesscontrol.windows.net/{self.tenant_id}/tokens/OAuth/2"
        payload = {
            "grant_type": "client_credentials",
            "client_id": f"{self.client_id}@{self.tenant_id}",
            "client_secret": self.client_secret,
            "resource": resource,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
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
        try:
            self.credentials = await self._load_credentials()
            site_url = f"https://{self.tenant_name}.sharepoint.com"

            self.base_headers = {
                "Authorization": f"Bearer {self.credentials['access_token']}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            self.base_url = f"{site_url}/sites/{self.site_name}/_api/"
            connector = TCPConnector(ssl=ssl_context)
            self.session = ClientSession(
                headers=self.base_headers, base_url=self.base_url, connector=connector
            )
            return self
        except ClientError as error:
            raise ConnectionError(error)

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
            endpoint = f"web/{folder_relative_url}/Folders"
            response = await self.session.get(endpoint.lstrip("/"))
            response.raise_for_status()
            response_json = await response.json()
            return response_json
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
            data = args.file_content

            endpoint = f"web/{folder_relative_url}/Files/add(url='{args.file_name}',overwrite=true)"
            response = await self.session.post(endpoint, data=data, headers=headers)

            response.raise_for_status()
            return await response.json()
        except ClientError as error:
            raise ConnectionError(error) from error

    async def create_folder(self, args: SpCreateFolderArgs):
        try:
            # Load form digest value
            form_digest_value = await self._load_form_digest_value()
            headers = {
                **self.base_headers,
                "X-RequestDigest": form_digest_value,
            }
            body = {"ServerRelativeUrl": f"{args.folder_relative_url}"}
            endpoint = "web/folders"
            response = await self.session.post(
                endpoint.lstrip("/"), data=json.dumps(body), headers=headers
            )
            response.raise_for_status()
            response_json = await response.json()
            return response_json
        except ClientError as error:
            raise ConnectionError(error) from error
