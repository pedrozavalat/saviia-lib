from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class CloudClientInitArgs:
    config: Any
    client_name: Literal["sharepoint_rest_api", "databricks"] = "databricks"


@dataclass
class CloudClientListFilesArgs:
    folder_relative_url: str


@dataclass
class CloudClientListFoldersArgs:
    folder_relative_url: str


@dataclass
class CloudClientUploadFileArgs:
    folder_relative_url: str
    file_name: str
    file_content: bytes = bytes()


@dataclass
class CloudClientCreateFolderArgs:
    folder_relative_url: str


@dataclass
class CloudClientResolveUrlArgs:
    folder_path: str