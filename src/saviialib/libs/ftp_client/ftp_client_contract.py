from abc import ABC, abstractmethod

from .types.ftp_client_types import FtpListFilesArgs, FtpReadFileArgs


class FTPClientContract(ABC):
    @abstractmethod
    def list_files(self, args: FtpListFilesArgs) -> list[str]:
        pass

    @abstractmethod
    def read_file(self, args: FtpReadFileArgs) -> bytes:
        pass
