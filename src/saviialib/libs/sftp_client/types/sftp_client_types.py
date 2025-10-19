from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class SFTPClientInitArgs:
    client_name: str
    password: Optional[str]
    username: str
    ssh_key_path: str
    host: str = "localhost"
    port: int = 22


@dataclass
class ListfilesArgs:
    path: str


@dataclass
class DownloadfilesArgs:
    source_path: str
    destination_path: str
    files_to_download: List[str] = field(default_factory=list)
