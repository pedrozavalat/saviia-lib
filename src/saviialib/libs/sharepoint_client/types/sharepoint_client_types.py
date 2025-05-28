from dataclasses import dataclass
from typing import Any


@dataclass
class SharepointClientInitArgs:
    config: Any
    client_name: str = "sharepoint_rest_api"


@dataclass
class SpListFilesArgs:
    folder_relative_url: str


@dataclass
class SpListFoldersArgs:
    folder_relative_url: str


@dataclass
class SpUploadFileArgs:
    folder_relative_url: str
    file_name: str
    file_content: bytes = bytes()


@dataclass
class SpCreateFolderArgs:
    folder_relative_url: str
