from .types.get_camera_rates_types import (
    GetCameraRatesUseCaseInput,
    GetCameraRatesUseCaseOutput,
)

from saviialib.libs.weather_client import ForecastArgs, WeatherQuery, WeatherMetric
from saviialib.libs.zero_dependency.utils.datetime_utils import today, datetime_to_str
from saviialib.libs.log_client import LogClient, LogClientArgs, DebugArgs, LogStatus
import saviialib.services.netcamera.constants.get_camera_rates_constants as c


class GetCameraRatesUseCase:
    def __init__(self, input: GetCameraRatesUseCaseInput) -> None:
        self.weather_client = input.weather_client
        self.logger = LogClient(
            LogClientArgs(
                client_name="logging",
                service_name="netcamera",
                class_name="get_camera_rates",
            )
        )

    def _get_status(self, curr_prob: float, curr_prec: float) -> str:
        self.logger.method_name = "_get_status"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        if (curr_prob is None) or (curr_prec is None):
            self.logger.debug(DebugArgs(LogStatus.EARLY_RETURN))
            return ""
        for case in c.PRECIPITATION_MATRIX:
            prob_min, prob_max, prec_min, prec_max, status = case
            if prob_min <= curr_prob <= prob_max and prec_min <= curr_prec <= prec_max:
                self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
                self.logger.method_name = "execute"
                return status
        self.logger.debug(DebugArgs(LogStatus.ALERT))
        raise KeyError("Precipitation and probability values out of range.")

    async def execute(self) -> GetCameraRatesUseCaseOutput:
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(LogStatus.STARTED))

        now = datetime_to_str(today(), date_format="%Y-%m-%dT%H:00")
        response = await self.weather_client.forecast(
            ForecastArgs(
                WeatherQuery(WeatherMetric.PRECIPITATION_PROB),
                start_date=datetime_to_str(today(), date_format="%Y-%m-%d"),
                end_date=datetime_to_str(today(), date_format="%Y-%m-%d"),
            )
        )
        curr_prob = response["precipitation_probability"].get(now, None)
        response = await self.weather_client.forecast(
            ForecastArgs(
                query=WeatherQuery(metric=WeatherMetric.PRECIPITATION),
                start_date=datetime_to_str(today(), date_format="%Y-%m-%d"),
                end_date=datetime_to_str(today(), date_format="%Y-%m-%d"),
            )
        )
        curr_prec = response["precipitation"].get(now, None)
        status = self._get_status(curr_prob, curr_prec)
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return GetCameraRatesUseCaseOutput(
            status,
            photo_rate=c.CAPTURE_TIMES[status]["photo"],
            video_rate=c.CAPTURE_TIMES[status]["video"],
        )
