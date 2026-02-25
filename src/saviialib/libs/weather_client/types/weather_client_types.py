from dataclasses import dataclass
from typing import Optional, Literal
from enum import Enum


@dataclass
class WeatherClientInitArgs:
    client_name: Literal["open_meteo"]
    latitude: float
    longitude: float
    timezone: str = ""
    api_key: Optional[str] = ""


class WeatherMetric(Enum):
    AIRTEMP = "air_temperature"
    CO2 = "c02"
    HUMIDITY = "humidity"
    PICOSOILTEMP1 = "pico_soil_temperature_1"
    PICOMOISTURE1 = "pico_moisture_1"
    PRECIPITATION = "precipitation"
    PRECIPITATION_PROB = "precipitation_probability"
    PRESSURE = "pressure"
    RADIATION = "global_radiation"
    WS = "wind_speed"
    WD = "wind_direction"
    # TODO: add PAR, UVA and UVB radiation.
    # TODO: add PRTEMP = "pressure_temperature"


@dataclass
class WeatherQuery:
    metric: WeatherMetric
    show_aggregates: bool = False


@dataclass
class ForecastArgs:
    query: WeatherQuery
    start_date: Optional[int | str | float]
    end_date: Optional[int | str | float]
