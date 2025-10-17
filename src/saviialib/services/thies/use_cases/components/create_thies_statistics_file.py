from .thies_bp import THIESDayData
from logging import Logger
from asyncio import to_thread
from saviialib.libs.directory_client import DirectoryClient
from saviialib.libs.zero_dependency.utils.datetime_utils import datetime_to_str, today
from saviialib.libs.files_client import FilesClient, FilesClientInitArgs, WriteArgs


AVG_COLUMNS = {
    "Date": "date",
    "Time": "time",
    "AirTemperature": "air_temperature",
    "Radiation": "radiation",
    "CO2": "carbon_dioxide",
    "Precipitation": "precipitation",
    "WS": "wind_velocity",
    "WD": "wind_direction",
    "Humidity": "humidity",
}

EXT_COLUMNS = {
    "Date": "date",
    "Time": "time",
    "AirTemperature MIN": "air_temperature",
    "AirTemperature MAX": "air_temperature",
    "Radiation MIN": "radiation",
    "Radiation MAX": "radiation",
    "CO2 MIN": "carbon_dioxide",
    "CO2 MAX": "carbon_dioxide",
    "WS MIN": "wind_velocity",
    "WS MAX gust": "wind_velocity",
    "WD MIN": "wind_direction",
    "WD MAX gust": "wind_direction",
    "Humidity MIN": "humidity",
    "Humidity MAX": "humidity",
}

AGG_DICT = {
    "AirTemperature": "mean",
    "AirTemperature MIN": "mean",
    "AirTemperature MAX": "mean",
    "Precipitation": "sum",
    "Humidity": "mean",
    "Humidity MIN": "mean",
    "Humidity MAX": "mean",
    "Radiation": "sum",
    "Radiation MIN": "sum",
    "Radiation MAX": "sum",
    "CO2": "sum",
    "CO2 MIN": "sum",
    "CO2 MAX": "sum",
    "WS": "mean",
    "WS MIN": "mean",
    "WS MAX gust": "mean",
    "WD": "mean",
    "WD MIN": "mean",
    "WD MAX gust": "mean",
}

UNITS = {
    "AirTemperature": "°C",
    "Precipitation": "mm",
    "Humidity": "%",
    "Radiation": "W/m2",
    "CO2": "ppm",
    "WS": "m/s",
    "WD": "°",
}


async def create_thies_daily_statistics_file(
    os_client: DirectoryClient, logger: Logger
) -> None:
    logger.debug("[thies_synchronization_lib] Creating Daily Statistics ...")
    csv_client = FilesClient(FilesClientInitArgs(client_name="csv_client"))
    filename = datetime_to_str(today(), date_format="%Y%m%d") + ".BIN"
    path_bin_av = os_client.join_paths("thies-daily-files", "ARCH_AV1", filename)
    path_ini_av = os_client.join_paths("thies-daily-files", "ARCH_AV1", "DESCFILE.INI")
    path_bin_ex = os_client.join_paths("thies-daily-files", "ARCH_EX1", filename)
    path_ini_ex = os_client.join_paths("thies-daily-files", "ARCH_EX1", "DESCFILE.INI")

    ext_df = THIESDayData("ex")
    await to_thread(ext_df.read_binfile, path_bin_ex, path_ini_ex)

    avg_df = THIESDayData("av")
    await to_thread(avg_df.read_binfile, path_bin_av, path_ini_av)

    ext_df = ext_df.dataDF[EXT_COLUMNS.keys()]
    avg_df = avg_df.dataDF[AVG_COLUMNS.keys()]

    # Merge both dataframes
    df = avg_df.merge(ext_df, on=["Date", "Time"], how="outer")
    # Set the date as dd.mm.yyyy format.
    df["Date"] = df["Date"].str.replace(
        r"(\d{4})/(\d{2})/(\d{2})", r"\3.\2.\1", regex=True
    )
    df["Hour"] = df["Time"].str[:2]

    # Group by hour.
    hourly_agg = df.groupby(["Date", "Hour"]).agg(AGG_DICT).reset_index()

    rows = []
    # For each attribute in avg_columns (except Date, Time)
    for col, col_id in AVG_COLUMNS.items():
        if col in ["Date", "Time"]:
            continue
        # Determine the corresponding min/max columns if they exist
        min_col = f"{col} MIN"
        max_col = f"{col} MAX"
        mean_col = col
        if col in ["WS", "WD"]:
            max_col += " gust"

        unit = UNITS.get(col, "")

        for idx, row in hourly_agg.iterrows():
            statistic_id = f"sensor.saviia_epii_{col_id}"
            start = f"{row['Date']} {row['Hour']}:00"
            mean = row[mean_col] if mean_col in row else 0
            min_val = row[min_col] if min_col in row else 0
            max_val = row[max_col] if max_col in row else 0

            # If no min/max for this attribute is 0
            if min_col not in row:
                min_val = 0
            if max_col not in row:
                max_val = 0

            if (mean < min_val or mean > max_val) and col not in ["WD"]:
                logger.warning(
                    f"[thies_synchronization_lib] Inconsistent data for {col}: "
                    f"min {min_val}, max {max_val}, mean {mean}. "
                )
                mean = (min_val + max_val) / 2
                logger.warning(
                    f"[thies_synchronization_lib] Mean value corrected to {mean}."
                )

            if col in ["WD"]:  # Avoid error
                rows.append(
                    {
                        "statistic_id": statistic_id,
                        "unit": unit,
                        "start": start,
                        "min": mean,
                        "max": mean,
                        "mean": mean,
                    }
                )
            else:
                rows.append(
                    {
                        "statistic_id": statistic_id,
                        "unit": unit,
                        "start": start,
                        "min": min_val,
                        "max": max_val,
                        "mean": mean,
                    }
                )

    logger.debug("[thies_synchronization_lib] Saving file in /config folder ...")
    logger.debug(rows[0].keys())
    await csv_client.write(
        WriteArgs(file_name="thies_daily_statistics.tsv", file_content=rows, mode="w")
    )
    logger.debug(
        "[thies_synchronization_lib] thies_daily_statistics.tsv created successfully!"
    )
