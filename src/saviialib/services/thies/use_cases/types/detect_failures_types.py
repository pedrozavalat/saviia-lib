from dataclasses import dataclass
from saviialib.db import DbClient
from saviialib.libs.weather_client import WeatherClient


@dataclass
class DetectFailuresUseCaseInput:
    local_backup_source_path: str
    db_client: DbClient
    weather_client: WeatherClient


@dataclass
class DetectFailuresUseCaseOutput:
    result: dict