from dataclasses import dataclass
from saviialib.libs.weather_client import WeatherClient


@dataclass
class GetCameraRatesUseCaseInput:
    weather_client: WeatherClient


@dataclass
class GetCameraRatesUseCaseOutput:
    status: str
    photo_rate: int
    video_rate: int
