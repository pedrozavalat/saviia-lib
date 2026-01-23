from dataclasses import dataclass, field
from typing import Dict
from saviialib.general_types.api.saviia_netcamera_api_types import SaviiaNetcameraConfig


@dataclass
class GetCameraRatesControllerInput:
    config: SaviiaNetcameraConfig


@dataclass
class GetCameraRatesControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
