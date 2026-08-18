from logging import Logger
from typing import Any, Dict, List, Set, cast

from saviialib.general_types.error_types.api.saviia_api_error_types import (
    CloudClientUploadError,
)
from saviialib.general_types.error_types.common import CloudClientError
from saviialib.libs.cloud_client import CloudClientUploadFileArgs
from saviialib.libs.files_client import ReadArgs
from saviialib.libs.log_client import LogStatus

from .base import ThiesComponent
from .paths import ThiesCategory, ThiesPathComponent


class ThiesCloudSyncComponent(ThiesComponent):
    """Read pending local THIES files and upload them to cloud storage."""

    def __init__(
        self,
        paths: ThiesPathComponent,
        files_client: Any,
        cloud_client: Any,
        logger: Logger | None = None,
    ) -> None:
        super().__init__("thies_cloud_sync", logger)
        self.paths = paths
        self.files_client = files_client
        self.cloud_client = cloud_client

    async def read_local_files(self, file_keys: Set[str]) -> Dict[str, bytes]:
        method_name = "read_local_files"
        self._debug(
            method_name,
            LogStatus.STARTED,
            f"Loading content for {len(file_keys)} pending files",
        )
        contents: Dict[str, bytes] = {}
        for file_key in file_keys:
            category_value, filename = file_key.split("_", 1)
            category = cast(ThiesCategory, category_value)
            local_folder = self.paths.get_local_folder(category)
            file_path = f"{local_folder}/{filename}"
            contents[file_key] = await self.files_client.read(
                ReadArgs(file_path=file_path, mode="rb")
            )
            self._debug(
                method_name,
                LogStatus.SUCCESSFUL,
                f"Loaded local file '{file_key}' from '{file_path}'",
            )
        return contents

    async def upload_files(self, files: Dict[str, bytes]) -> Dict[str, List[str]]:
        method_name = "upload_files"
        if self.cloud_client is None:
            raise CloudClientError("SAVIIA Cloud client provider was not initialized.")

        results: Dict[str, List[str]] = {"failed_files": [], "new_files": []}
        self._debug(
            method_name,
            LogStatus.STARTED,
            f"Uploading {len(files)} files under '{self.paths.get_cloud_thies_path()}'",
        )
        async with self.cloud_client:
            for file_key, content in files.items():
                category_value, filename = file_key.split("_", 1)
                category = cast(ThiesCategory, category_value)
                destination = self.paths.get_cloud_folder(category)
                try:
                    await self.cloud_client.upload_file(
                        CloudClientUploadFileArgs(
                            folder_relative_url=destination,
                            file_content=content,
                            file_name=filename,
                        )
                    )
                    results["new_files"].append(file_key)
                    self._debug(
                        method_name,
                        LogStatus.SUCCESSFUL,
                        f"Uploaded '{filename}' to '{destination}'",
                    )
                except ConnectionError as error:
                    self._error(
                        method_name,
                        f"Failed to upload '{filename}' to '{destination}'",
                        error,
                    )
                    results["failed_files"].append(
                        f"{file_key} (Error: {str(error)})"
                    )

        if results["failed_files"]:
            raise CloudClientUploadError(
                reason="Files failed to upload: " + ", ".join(results["failed_files"])
            )
        return results
