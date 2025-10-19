from dataclasses import dataclass
from logging import Logger


@dataclass
class SaviiaNetcameraConfig:
    username: str
    password: str
    protocol: str
    logger: Logger
    destination_path: str = "/"
