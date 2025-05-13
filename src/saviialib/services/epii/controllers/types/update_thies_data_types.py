from dataclasses import dataclass, field
from typing import Dict
from saviialib.general_types.api.epii_api_types import (
    EpiiUpdateThiesConfig,
)


@dataclass
class UpdateThiesDataControllerInput:
    config: EpiiUpdateThiesConfig


@dataclass
class UpdateThiesDataControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
