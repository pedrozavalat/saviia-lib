from typing import Any
from urllib.parse import quote

from aiohttp import ClientError, ClientSession

from saviialib.libs.cloud_client.cloud_client_contract import CloudClientContract
from saviialib.libs.cloud_client.types.cloud_client_types import (
    CloudClientCreateFolderArgs,
    CloudClientInitArgs,
    CloudClientListFilesArgs,
    CloudClientListFoldersArgs,
    CloudClientResolveUrlArgs,
    CloudClientUploadFileArgs,
)


class DatabricksClient(CloudClientContract):
    def __init__(self, args: CloudClientInitArgs):
        self.session: ClientSession | None = None
        self.api_key = args.config.databricks_api_key

        required = {
            "databricks_api_key": self.api_key,
            "databricks_host_url": args.config.databricks_host_url,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing Databricks config fields: {', '.join(missing)}")

        self.host_url = args.config.databricks_host_url.rstrip("/")
        self.base_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    async def __aenter__(self) -> "DatabricksClient":
        self.session = ClientSession(base_url=self.host_url, headers=self.base_headers)
        return self

    async def __aexit__(
        self, _exc_type: type[BaseException], _exc_val: BaseException, _exc_tb: Any
    ) -> None:
        if self.session:
            await self.session.close()

    @property
    def base_url(self):
        return self.host_url

    async def list_files(self, args: CloudClientListFilesArgs) -> list:
        try:
            path = quote(args.folder_relative_url, safe="/")
            endpoint = f"/api/2.0/fs/directories{path}"
            response = await self.session.get(endpoint)
            response.raise_for_status()
            payload = await response.json()
            return payload.get("contents", [])
        except ClientError as error:
            raise ConnectionError(error) from error

    async def list_folders(self, args: CloudClientListFoldersArgs) -> list:
        try:
            contents = await self.list_files(
                CloudClientListFilesArgs(folder_relative_url=args.folder_relative_url)
            )
            return [item for item in contents if item.get("is_directory") is True]
        except ClientError as error:
            raise ConnectionError(error) from error

    async def upload_file(self, args: CloudClientUploadFileArgs) -> dict:
        try:
            dest_path = f"{args.folder_relative_url.rstrip('/')}/{args.file_name}"
            path = quote(dest_path, safe="/")
            endpoint = f"/api/2.0/fs/files{path}?overwrite=true"
            headers = {**self.base_headers, "Content-Type": "application/octet-stream"}

            response = await self.session.put(
                endpoint,
                data=args.file_content,
                headers=headers,
            )
            response.raise_for_status()

            if response.status == 204:
                return {
                    "status": response.status,
                    "path": dest_path,
                    "message": "uploaded",
                }

            return await response.json()
        except ClientError as error:
            raise ConnectionError(error) from error

    async def create_folder(self, args: CloudClientCreateFolderArgs) -> dict:
        try:
            path = quote(args.folder_relative_url, safe="/")
            endpoint = f"/api/2.0/fs/directories{path}"
            response = await self.session.put(endpoint)
            response.raise_for_status()

            if response.status == 204:
                return {
                    "status": response.status,
                    "path": args.folder_relative_url,
                    "message": "created",
                }

            return await response.json()
        except ClientError as error:
            raise ConnectionError(error) from error

    def resolve_url(self, args: CloudClientResolveUrlArgs) -> str:
        return args.folder_path.rstrip("/")
