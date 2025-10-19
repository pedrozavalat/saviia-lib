from dataclasses import dataclass
from typing import Dict
from saviialib.general_types.api.saviia_shakes_api_types import SaviiaShakesConfig


@dataclass
class GetMiniseedFilesControllerInput:
    raspberry_shakes: Dict[str, str]
    config: SaviiaShakesConfig


@dataclass
class GetMiniseedFilesControllerOutput:
    status: int
    metadata: Dict
    message: str
