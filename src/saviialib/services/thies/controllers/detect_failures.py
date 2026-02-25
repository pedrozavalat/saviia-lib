from http import HTTPStatus
from saviialib.services.thies.controllers.types.detect_failures_types import (
    DetectFailuresControllerInput,
    DetectFailuresControllerOutput,
)
from .types.detect_failures_schema import DETECT_FAILURES_SCHEMA
from saviialib.services.thies.use_cases.detect_failures import DetectFailuresUseCase
from saviialib.services.thies.use_cases.types.detect_failures_types import (
    DetectFailuresUseCaseInput,
)

from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.db import DbClient, DbClientInitArgs
from saviialib.libs.weather_client import WeatherClient, WeatherClientInitArgs


class DetectFailuresController:
    def __init__(self, input: DetectFailuresControllerInput):
        self.input = input
        self.weather_client = WeatherClient(
            WeatherClientInitArgs(
                client_name="open_meteo",
                latitude=input.config.latitude,
                longitude=input.config.longitude,
            )
        )
        self.db_client = DbClient(
            DbClientInitArgs(
                client_name="pyodbc_client",
                connection_string=(
                    f"driver={input.db_driver};"
                    f"server={input.db_host};"
                    f"database={input.db_name};"
                    f"uid={input.user};"
                    f"pwd={input.pwd}"
                ),
            )
        )

    async def _connect_clients(self) -> None:
        await self.weather_client.connect()
        # await self.db_client.connect()

    async def _close_clients(self) -> None:
        await self.weather_client.close()
        # await self.db_client.close()

    async def execute(self) -> DetectFailuresControllerOutput:
        try:
            SchemaValidatorClient(schema=DETECT_FAILURES_SCHEMA).validate(
                {
                    "local_backup_source_path": self.input.local_backup_source_path,
                    "db_driver": self.input.db_driver,
                    "db_host": self.input.db_host,
                    "db_name": self.input.db_name,
                    "user": self.input.user,
                    "pwd": self.input.pwd,
                    "n_days": self.input.n_days,
                }
            )
            await self._connect_clients()
            use_case = DetectFailuresUseCase(
                DetectFailuresUseCaseInput(
                    local_backup_source_path=self.input.local_backup_source_path,
                    db_client=self.db_client,
                    weather_client=self.weather_client,
                    n_days=self.input.n_days,
                )
            )
            output = await use_case.execute()
            if output.validation == {}:
                return DetectFailuresControllerOutput(
                    message="The /thies folder was empty.",
                    status=HTTPStatus.NO_CONTENT.value,
                    metadata=output.__dict__,
                )
            return DetectFailuresControllerOutput(
                message="The validation was successful.",
                status=HTTPStatus.OK.value,
                metadata=output.__dict__,
            )

        except (AttributeError, NameError, ValueError) as error:
            return DetectFailuresControllerOutput(
                message="An unexpected error occurred during use case initialization.",
                status=HTTPStatus.BAD_REQUEST.value,
                metadata={"error": error.__str__()},
            )

        except (ConnectionError, RuntimeError) as error:
            return DetectFailuresControllerOutput(
                message="The connection could not bet established.",
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                metadata={"error": error.__str__()},
            )
