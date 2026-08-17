from abc import ABC, abstractmethod

from .types.cloud_client_types import (
    CloudClientListFilesArgs,
    CloudClientListFoldersArgs,
    CloudClientUploadFileArgs,
    CloudClientCreateFolderArgs,
    CloudClientResolveUrlArgs,
)


class CloudClientContract(ABC):
    @property
    def base_url(self):
        pass
    
    @abstractmethod
    async def list_files(self, args: CloudClientListFilesArgs) -> list:
        pass

    @abstractmethod
    async def list_folders(self, args: CloudClientListFoldersArgs) -> list:
        pass

    @abstractmethod
    async def upload_file(self, args: CloudClientUploadFileArgs) -> dict:
        pass

    @abstractmethod
    async def create_folder(self, args: CloudClientCreateFolderArgs) -> dict:
        pass

    @abstractmethod
    def resolve_url(self, args: CloudClientResolveUrlArgs) -> str:
        pass
