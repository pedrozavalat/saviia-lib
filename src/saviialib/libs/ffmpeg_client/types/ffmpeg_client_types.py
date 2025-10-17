from dataclasses import dataclass


@dataclass
class FfmpegClientInitArgs:
    client_name: str


@dataclass
class RecordPhotoArgs:
    ip_address: str
    destination_path: str
    rtsp_user: str
    rtsp_password: str
    port: str
    extension: str
    frames: int


@dataclass
class RecordVideoArgs:
    destination_path: str
    ip_address: str
    port: str
    rtsp_user: str
    rtsp_password: str
    extension: str
    duration: int
