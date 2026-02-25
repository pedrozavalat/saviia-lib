from .types.detect_failures_types import (
    DetectFailuresUseCaseInput,
    DetectFailuresUseCaseOutput,
)
import pandas as pd
from saviialib.libs.log_client import LogClient, LogClientArgs, LogStatus, DebugArgs
from .components.thies_bp import THIESDayData
from saviialib.libs.zero_dependency.utils.datetime_utils import (
    today,
    difference,
    str_to_datetime,
    datetime_to_str,
)
import saviialib.services.thies.constants.detect_failures_constants as const
from saviialib.libs.files_client import ReadArgs, FilesClientInitArgs, FilesClient
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.weather_client import WeatherMetric, WeatherQuery, ForecastArgs
import math


class DetectFailuresUseCase:
    def __init__(self, input: DetectFailuresUseCaseInput) -> None:
        self.db_client = input.db_client
        self.weather_client = input.weather_client
        self.file_client = FilesClient(
            FilesClientInitArgs(client_name="aiofiles_client")
        )
        self.dir_client = DirectoryClient(DirectoryClientArgs(client_name="os_client"))
        self.logger = LogClient(
            LogClientArgs(service_name="tasks", class_name="delete_task")
        )
        self.start_date = difference(today(), input.n_days)
        self.end_date = today()
        self.root = self.dir_client.join_paths(input.local_backup_source_path, "thies")
        self.columns_to_keep = []
        for attr, aggr in const.COLS_TO_KEEP.items():
            if aggr != ():  # mean, min, max
                self.columns_to_keep.extend(
                    [attr, f"{attr} {aggr[0]}", f"{attr} {aggr[1]}"]
                )
            else:  # mean
                self.columns_to_keep.append(attr)

    def _file_in_range(self, filename: str) -> bool:
        date_token = filename.split(".", 1)[0]
        try:
            filename_date = str_to_datetime(date_token, date_format="%Y%m%d").date()
        except ValueError:
            return False
        return self.start_date.date() <= filename_date <= self.end_date.date()

    async def _download_last_files_info(self) -> tuple[pd.DataFrame, set[str]]:
        self.logger.method_name = "_download_last_files_info"
        file_spath = self.dir_client.join_paths(self.root, "AVG")  # Could be EXT too.
        filtered_files = {
            f.split(".")[0]  # Remove the type .BIN
            for f in await self.dir_client.listdir(file_spath)
            if self._file_in_range(f)
        }
        self.logger.debug(DebugArgs(LogStatus.STARTED, {"msg": filtered_files}))
        data = pd.DataFrame()
        for file in filtered_files:
            merged_df = pd.DataFrame()
            for prefix in ["AVG", "EXT"]:
                dtype = "av" if prefix == "AVG" else "ex"
                df = THIESDayData(dtype)
                dir_path = self.dir_client.join_paths(self.root, prefix, file + ".BIN")
                dir_path_ini = self.dir_client.join_paths(
                    self.root, prefix, "DESCFILE.INI"
                )
                df.read_binfile(dir_path, dir_path_ini)
                merged_df = (
                    df.dataDF
                    # 1: df = avg df
                    if prefix == "AVG"
                    # 2: df = ext df
                    else merged_df.merge(df.dataDF, on=["Date", "Time"], how="outer")
                )
            data = pd.concat([data, self._filter_data(merged_df)], ignore_index=True)
        data = self._preprocess_data(data)
        last_dates = {f"{file[0:4]}-{file[4:6]}-{file[6:]}" for file in filtered_files}
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return data, last_dates

    def _filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.columns_to_keep]

    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.method_name = "_preprocess_data"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        # Filter and keep columns
        df["Date"] = df["Date"].str.replace(
            r"(\d{4})/(\d{2})/(\d{2})", r"\1-\2-\3", regex=True
        )
        df["Hour"] = df["Time"].str[:2]
        # Extract the hourly for each attribute, except date and time.
        attrs = [c for c in self.columns_to_keep if c not in ("Date", "Time", "Hour")]
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return (
            df.groupby(["Date", "Hour"])
            .agg({attr: "mean" for attr in attrs})
            .reset_index()
        )

    def _extract_threshold_weather_client(
        self, res: dict, date: str
    ) -> tuple[float | None, float | None]:
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        aggrs = res["aggregations"]
        low, high = None, None
        for aggr, values in aggrs.items():
            if "dominant" in aggr or "max" in aggr:
                high = values[date]
            elif "min" in aggr:
                low = values[date]
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL, {'msg': f'Min: {low}, Max: {high}'}))
        return low, high

    async def _validate_threshold_against_weather_client(
        self, data: pd.DataFrame, last_dates: set[str]
    ) -> dict:
        """Validate for each hour."""
        self.logger.method_name = "_validate_threshold_against_weather_client"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        date_format = "%Y-%m-%d"
        start_date_str, end_date_str = (
            datetime_to_str(self.start_date, date_format),
            datetime_to_str(self.end_date, date_format),
        )
        validation = {}
        for attr, aggr in const.COLS_TO_KEEP.items():
            if attr in ("Date", "Time", "Hour"):
                continue
            attrs = [attr]
            if aggr != ():
                # Min, Max
                attrs.extend([f"{attr} {aggr[0]}", f"{attr} {aggr[1]}"])
            # Extract all the data from weather client between start and end date.
            res = await self.weather_client.forecast(
                ForecastArgs(
                    WeatherQuery(
                        metric=const.METRIC_TO_WEATHER_PARAM[attrs[0]],
                        show_aggregates=True,
                    ),
                    start_date_str,
                    end_date_str,
                )
            )
            days_with_failures, total_days = 0, len(last_dates)
            majority = total_days // 2 + 1
            exceeds_majority = False
            cnt_out_of_bound, cnt_all_zeros = 0, 0
            for date in last_dates:
                # Validate if any value is out of bounds.
                low, high = self._extract_threshold_weather_client(res, date)
                daily_data = data[(data["Date"] == date)][attr].dropna()
                if daily_data.empty:
                    continue
                # Exception for Wind speed: dominant aggregation
                if attr == "WD":
                    daily_data = data[(data["Date"] == date)][attrs[2]]
                    out_of_bound = daily_data[(daily_data > high)]
                else:
                    out_of_bound = daily_data[
                        (daily_data < low)  # under the lowest
                        | (daily_data > high)  # or above the highest
                    ]
                if attr == "WS": 
                    pass
                violations = out_of_bound.count() / daily_data.count()
                # Validate is all the values are zero.
                all_zeros = (daily_data == 0).all()
                # Check if one constraint breaks
                break_constraints = violations > const.UMBRAL or all_zeros
                if violations > const.UMBRAL:
                    cnt_out_of_bound += 1
                if all_zeros:
                    cnt_all_zeros += 1
                if break_constraints:
                    days_with_failures += 1
            exceeds_majority = days_with_failures > majority
            self.logger.debug(
                DebugArgs(
                    LogStatus.SUCCESSFUL,
                    {
                        "msg": f"Sensor related to {attr} failed?: {exceeds_majority}"
                    },
                )
            )
            validation[attr] = {
                "sensor_failed": exceeds_majority,
                "considered_param": attr,
                "days_with_failures": days_with_failures,
                "days_out_of_bound": cnt_out_of_bound,
                "days_all_zeros": cnt_all_zeros,
            }

        return validation

    def _parse_metrics_to_sensors(self, weather_val: dict, saviia_val: dict) -> dict:
        return {const.METRICS_TO_SENSORS[k]: v for k, v in weather_val.items()}

    async def _validate_threshold_against_saviia(
        self, data: pd.DataFrame, last_dates: set[str]
    ) -> dict:
        """Not implemented yet."""
        self.logger.method_name = "_validate_threshold_against_saviia"
        self.logger.debug(DebugArgs(LogStatus.ALERT, {"msg": "Not implemented yet."}))
        return {}

    async def execute(self) -> DetectFailuresUseCaseOutput:
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        data, last_dates = await self._download_last_files_info()
        saviia_val = await self._validate_threshold_against_saviia(data, last_dates)
        weather_val = await self._validate_threshold_against_weather_client(
            data, last_dates
        )
        # TODO: Check both results and merge them.
        validation = self._parse_metrics_to_sensors(weather_val, saviia_val)
        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return DetectFailuresUseCaseOutput(validation)
