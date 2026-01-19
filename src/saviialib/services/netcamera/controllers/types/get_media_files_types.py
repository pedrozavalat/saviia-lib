from dataclasses import dataclass, field
from typing import Dict, Tuple
from saviialib.general_types.api.saviia_netcamera_api_types import SaviiaNetcameraConfig


@dataclass
class GetMediaFilesControllerInput:
    config = SaviiaNetcameraConfig
    cameras: Dict[str, Tuple[str, int]]


@dataclass
class GetMediaFilesControllerOutput:
    status: int
    message: str
    metadata: Dict = field(default_factory=dict)
