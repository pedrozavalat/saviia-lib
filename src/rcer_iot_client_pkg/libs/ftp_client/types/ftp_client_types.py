from dataclasses import dataclass


@dataclass
class FtpClientInitArgs:
    host: str
    user: str
    password: str
    client_name: str = "aioftp_client"
    port: int = 21


@dataclass
class FtpListFilesArgs:
    path: str


@dataclass
class FtpReadFileArgs:
    file_path: str
