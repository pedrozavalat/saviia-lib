from dataclasses import dataclass, field
from typing import Dict
from logging import Logger


@dataclass
class GetMiniseedFilesUseCaseInput:
    raspberry_shakes: Dict[str, str]
    username: str
    password: str
    ssh_key_path: str
    port: int
    logger: Logger


@dataclass
class GetMiniseedFilesUseCaseOutput:
    download_status: Dict[str, str] = field(default_factory=dict)
