from abc import ABC, abstractmethod

from .types.sharepoint_client_types import (
    SpListFilesArgs,
    SpListFoldersArgs,
    SpUploadFileArgs,
    SpCreateFolderArgs,
)


class SharepointClientContract(ABC):
    @abstractmethod
    async def list_files(self, args: SpListFilesArgs) -> list:
        pass

    @abstractmethod
    async def list_folders(self, args: SpListFoldersArgs) -> list:
        pass

    @abstractmethod
    async def upload_file(self, args: SpUploadFileArgs) -> dict:
        pass

    @abstractmethod
    async def create_folder(self, args: SpCreateFolderArgs) -> dict:
        pass
