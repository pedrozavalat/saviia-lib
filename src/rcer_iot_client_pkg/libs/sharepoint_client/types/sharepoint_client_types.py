from dataclasses import dataclass

@dataclass
class SharepointClientInitArgs:
    client_name: str = "sharepoint_rest_api"
    
@dataclass
class ListFilesArgs: 
    folder_relative_url: str
    
@dataclass
class ListFoldersArgs:
    folder_relative_url: str
    
@dataclass
class UploadFileArgs:
    file_path: str
    folder_relative_url: str
    file_content: bytes = bytes()