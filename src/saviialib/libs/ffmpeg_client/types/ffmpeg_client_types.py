from dataclasses import dataclass


@dataclass
class FfmpegClientInitArgs:
    client_name: str
    source_path: str


@dataclass
class RecordPhotoArgs:
    ip_address: str
    destination_path: str
    rtsp_user: str
    rtsp_password: str
    extension: str
    frames: int


@dataclass
class RecordVideoArgs:
    destination_path: str
    ip_address: str
    rtsp_user: str
    rtsp_password: str
    extension: str
    duration: int
