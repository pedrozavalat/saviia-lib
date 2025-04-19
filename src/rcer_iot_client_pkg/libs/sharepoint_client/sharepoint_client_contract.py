
from .types.sharepoint_client_types import ListFilesArgs, UploadFileArgs
from abc import ABC, abstractmethod

class SharepointClientContract(ABC):
    @abstractmethod
    async def list_files(self, args: ListFilesArgs) -> list:
        pass
    
    @abstractmethod
    async def list_folders(self, args: ListFilesArgs) -> list: 
        pass
    
    @abstractmethod
    async def upload_file(self, args: UploadFileArgs) -> dict: 
        pass