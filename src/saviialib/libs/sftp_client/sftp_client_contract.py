from .types.sftp_client_types import ListfilesArgs, DownloadfilesArgs
from abc import ABC, abstractmethod
from typing import List


class SFTPClientContract(ABC):
    @abstractmethod
    async def list_files(self, args: ListfilesArgs) -> List[str]:
        pass

    @abstractmethod
    async def download_files(self, args: DownloadfilesArgs) -> None:
        pass
