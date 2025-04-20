from dataclasses import dataclass, field
from typing import Dict
from rcer_iot_client_pkg.general_types.api.update_thies_data_types import EpiiAPIConfig


@dataclass
class UpdateThiesDataControllerInput:
    config: EpiiAPIConfig


@dataclass
class UpdateThiesDataControllerOutput:
    message: str
    status: int
    metadata: Dict[str, str] = field(default_factory=dict)
