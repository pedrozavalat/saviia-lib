from dataclasses import dataclass
from typing import Any


@dataclass
class FtpClientInitArgs:
    config: Any
    client_name: str = "aioftp_client"


@dataclass
class FtpListFilesArgs:
    path: str


@dataclass
class FtpReadFileArgs:
    file_path: str
