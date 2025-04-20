from dataclasses import dataclass


@dataclass
class SharepointClientInitArgs:
    client_name: str = "sharepoint_rest_api"


@dataclass
class SpListFilesArgs:
    folder_relative_url: str


@dataclass
class SpListFoldersArgs:
    folder_relative_url: str


@dataclass
class SpUploadFileArgs:
    file_path: str
    folder_relative_url: str
    file_content: bytes = bytes()
