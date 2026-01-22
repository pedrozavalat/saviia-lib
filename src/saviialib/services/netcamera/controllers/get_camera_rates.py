from .types.get_camera_rates_types import (
    GetCameraRatesControllerInput,
    GetCameraRatesControllerOutput,
)
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    ValidationError,
)
from http import HTTPStatus
from .types.get_camera_rates_schema import GET_CAMERA_RATES_SCHEMA
from saviialib.libs.weather_client import WeatherClient, WeatherClientInitArgs
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.services.netcamera.use_cases.types.get_camera_rates_types import (
    GetCameraRatesUseCaseInput,
)
from saviialib.services.netcamera.use_cases.get_camera_rates import (
    GetCameraRatesUseCase,
)
from saviialib.libs.log_client import LogClient, LogClientArgs, DebugArgs, LogStatus


class GetCameraRatesController:
    def __init__(self, input: GetCameraRatesControllerInput) -> None:
        self.input = input
        self.logger = LogClient(
            LogClientArgs(
                client_name="logging",
                service_name="netcamera",
                class_name="get_camera_rates_controller",
            )
        )
        self.weather_client = WeatherClient(
            WeatherClientInitArgs(
                client_name="open_meteo",
                latitude=input.latitude,
                longitude=input.longitude,
            )
        )

    async def _connect_clients(self) -> None:
        self.logger.method_name = "_connect_clients"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        await self.weather_client.connect()
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))

    async def _close_clients(self) -> None:
        self.logger.method_name = "_close_clients"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        await self.weather_client.close()
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))

    async def execute(self) -> GetCameraRatesControllerOutput:
        try:
            self.logger.method_name = "execute"
            self.logger.debug(DebugArgs(LogStatus.STARTED))
            SchemaValidatorClient(schema=GET_CAMERA_RATES_SCHEMA).validate(
                {
                    "latitude": self.input.latitude,
                    "longitude": self.input.longitude,
                }
            )
            await self._connect_clients()
            use_case = GetCameraRatesUseCase(
                GetCameraRatesUseCaseInput(
                    weather_client=self.weather_client,
                )
            )
            output = await use_case.execute()
            if not (output.video_rate and output.photo_rate):
                self.logger.debug(DebugArgs(LogStatus.EARLY_RETURN))
                return GetCameraRatesControllerOutput(
                    message="Could not determine camera rates based on the provided weather data.",
                    status=HTTPStatus.SERVICE_UNAVAILABLE.value,
                    metadata=output.__dict__,
                )
            return GetCameraRatesControllerOutput(
                message="Time rates for capture and recording were calculated successfully",
                status=HTTPStatus.OK.value,
                metadata=output.__dict__,
            )
        except ValidationError as error:
            self.logger.debug(DebugArgs(LogStatus.ALERT))
            return GetCameraRatesControllerOutput(
                message="Invalid input data.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )
        except ConnectionError as error:
            self.logger.debug(DebugArgs(LogStatus.ALERT))
            return GetCameraRatesControllerOutput(
                message="An unexpected error ocurred during client connection.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        except KeyError as error:
            self.logger.debug(DebugArgs(LogStatus.ALERT))
            return GetCameraRatesControllerOutput(
                message="An unexpected error occurred during use case execution",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
        finally:
            await self._close_clients()
            self.logger.method_name = "execute"
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
