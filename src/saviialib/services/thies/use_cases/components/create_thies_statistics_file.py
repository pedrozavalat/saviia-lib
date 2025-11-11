from .thies_bp import THIESDayData
import pandas as pd
from logging import Logger
from asyncio import to_thread
from saviialib.libs.directory_client import DirectoryClient
from saviialib.libs.zero_dependency.utils.datetime_utils import datetime_to_str, today
from saviialib.libs.files_client import FilesClient, FilesClientInitArgs, WriteArgs
import saviialib.services.thies.constants.update_thies_data_constants as c


async def create_thies_daily_statistics_file(
    local_backup_path: str, os_client: DirectoryClient, logger: Logger
) -> None:
    csv_client = FilesClient(FilesClientInitArgs(client_name="csv_client"))
    filename = datetime_to_str(today(), date_format="%Y%m%d") + ".BIN"
    logger.debug(
        f"[thies_synchronization_lib] Creating Daily Statistics for {filename}"
    )
    path_bin_av = os_client.join_paths(local_backup_path, "thies", "AVG", filename)
    path_ini_av = os_client.join_paths(
        local_backup_path, "thies", "AVG", "DESCFILE.INI"
    )
    path_bin_ex = os_client.join_paths(local_backup_path, "thies", "EXT", filename)
    path_ini_ex = os_client.join_paths(
        local_backup_path, "thies", "EXT", "DESCFILE.INI"
    )

    ext_df = THIESDayData("ex")
    await to_thread(ext_df.read_binfile, path_bin_ex, path_ini_ex)

    avg_df = THIESDayData("av")
    await to_thread(avg_df.read_binfile, path_bin_av, path_ini_av)

    ext_df = ext_df.dataDF[c.EXT_COLUMNS.keys()]
    avg_df = avg_df.dataDF[c.AVG_COLUMNS.keys()]

    # Merge both dataframes
    df = avg_df.merge(ext_df, on=["Date", "Time"], how="outer")
    # Set the date as dd.mm.yyyy format.
    df["Date"] = df["Date"].str.replace(
        r"(\d{4})/(\d{2})/(\d{2})", r"\3.\2.\1", regex=True
    )
    df["Hour"] = df["Time"].str[:2]

    # Group by hour.
    hourly_agg = df.groupby(["Date", "Hour"]).agg(c.AGG_DICT).reset_index()

    rows = []
    # For each attribute in avg_columns (except Date, Time)
    for col, col_id in c.AVG_COLUMNS.items():
        if col in ["Date", "Time"]:
            continue
        # Determine the corresponding min/max columns if they exist
        min_col = f"{col} MIN"
        max_col = f"{col} MAX"
        mean_col = col
        if col in ["WS", "WD"]:
            max_col += " gust"

        unit = c.UNITS.get(col, "")

        for idx, row in hourly_agg.iterrows():
            statistic_id = f"sensor.saviia_epii_{col_id}"
            start = f"{row['Date']} {row['Hour']}:00"
            mean = row[mean_col] if mean_col in row else 0
            min_val = row[min_col] if min_col in row else mean
            max_val = row[max_col] if max_col in row else mean

            # If no min/max for this attribute, set as Na or 0 as requested
            if not (pd.isna(mean) or pd.isna(min_val) or pd.isna(max_val)):
                pass
            elif pd.isna(mean) and not (pd.isna(min_val) or pd.isna(max_val)):
                mean = (min_val + max_val) / 2
            else:
                val_notna = [x for x in {mean, min_val, max_val} if not pd.isna(x)]
                if len(val_notna) >= 1:
                    mean_val = sum(val_notna) / len(val_notna)
                    mean = max_val = min_val = mean_val
                else:
                    continue  # Do not consider a row with null data

            # Normalize if the mean is upper than maxval or lower than minval
            if (mean < min_val or mean > max_val) and col not in ["WD"]:
                mean = (min_val + max_val) / 2

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

    logger.debug("[thies_synchronization_lib] Saving file in the main directory")
    await csv_client.write(
        WriteArgs(file_name="thies_daily_statistics.tsv", file_content=rows, mode="w")
    )
    logger.debug(
        "[thies_synchronization_lib] thies_daily_statistics.tsv created successfully!"
    )
