from .weather_client_contract import WeatherClientContract
from .types.weather_client_types import (
    ForecastArgs,
    WeatherClientInitArgs,
)
from .clients.openmeteo.openmeteo_client import OpenmeteoClient


class WeatherClient(WeatherClientContract):
    CLIENTS = {"open_meteo"}

    def __init__(self, args: WeatherClientInitArgs):
        if args.client_name not in WeatherClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)
        elif args.client_name == "open_meteo":
            self.client_obj = OpenmeteoClient(args)

    @property
    def latitude(self):
        return self.client_obj.latitude

    @property
    def longitude(self):
        return self.client_obj.longitude

    async def connect(self) -> None:
        return await self.client_obj.connect()

    async def close(self) -> None:
        return await self.client_obj.close()

    async def forecast(self, args: ForecastArgs):
        return await self.client_obj.forecast(args)

    def metrics(self) -> dict:
        return self.client_obj.metrics()
