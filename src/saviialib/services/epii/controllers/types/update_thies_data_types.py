from dataclasses import dataclass, field
from typing import Dict
from saviialib.general_types.api.update_thies_data_types import (
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
