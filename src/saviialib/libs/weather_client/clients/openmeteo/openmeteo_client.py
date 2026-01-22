from saviialib.libs.weather_client.types.weather_client_types import (
    ForecastArgs,
    WeatherClientInitArgs,
)
from saviialib.libs.weather_client.weather_client_contract import WeatherClientContract
from saviialib.libs.log_client import LogClient, LogClientArgs, DebugArgs, LogStatus
from aiohttp import ClientError, ClientSession, TCPConnector

from .openmeteo_constants import METRIC_MAP, DONT_SUPPORT_AGGR
import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())


class OpenmeteoClient(WeatherClientContract):
    def __init__(self, args: WeatherClientInitArgs) -> None:
        self._latitude = args.latitude
        self._longitude = args.longitude
        self._timezone = args.timezone
        self.session: ClientSession | None = None
        self.logger = LogClient(
            LogClientArgs(service_name="weather_client", class_name="openmeteo_client")
        )

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        self._latitude = value

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        self._longitude = value

    def _map_metric(self, metric_name: str):
        """Returns a dict of the metric and source api url for the data request"""
        metric = METRIC_MAP.get(metric_name, None)
        if metric is None:
            raise KeyError(
                f"The current metric '{metric_name}' is not supported for the current weather client"
            )
        return metric

    async def connect(self) -> None:
        if self.session:
            return
        self.session = ClientSession(connector=TCPConnector(ssl=ssl_context))

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def forecast(self, args: ForecastArgs):
        self.logger.method_name = "forecast"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        metric_name = args.query.metric.value
        metric = self._map_metric(metric_name)
        try:
            params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "start_date": args.start_date,
                "end_date": args.end_date,
            }
            can_show_aggrs = (
                args.query.show_aggregates and metric["name"] not in DONT_SUPPORT_AGGR
            )
            params["hourly"] = metric["name"]
            if can_show_aggrs:
                params["daily"] = ""
                for aggr in metric["aggr"]:
                    params["daily"] += f"{metric['name']}_{aggr},"
            params["timezone"] = self._timezone if self._timezone else "auto"
            res = await self.session.get(url=metric["source"], params=params)  # type: ignore
            resjson = await res.json()
            return {
                metric_name: list(
                    zip(resjson["hourly"]["time"], resjson["hourly"][metric["name"]])
                ),
                "aggregations": {
                    f"{metric['name']}_{aggr}": list(
                        zip(
                            resjson["daily"]["time"],
                            resjson["daily"][f"{metric['name']}_{aggr}"],
                        )
                    )
                    for aggr in metric["aggr"]
                }
                if can_show_aggrs
                else {},
            }
        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)

    def metrics(self) -> dict:
        return {
            name: {"aggregations": info.get("aggr", [])}
            for name, info in METRIC_MAP.items()
        }
