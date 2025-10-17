from dataclasses import dataclass
from logging import Logger
from typing import Dict, Tuple


@dataclass
class GetMediaFilesUseCaseInput:
    cameras: Dict[str, Tuple[str, int]]
    username: str
    password: str
    protocol: str
    logger: Logger
    destination_path: str


@dataclass
class GetMediaFilesUseCaseOutput:
    pass
