from typing import Any

from saviialib.libs.zero_dependency.utils.datetime_utils import (
    datetime_to_str,
    today,
)


def parse_execute_response(
    thies_fetched_files: dict[str, Any], upload_statistics: dict[str, Any]
) -> dict[str, dict[str, int | str]]:
    return {
        **upload_statistics,
        "processed_files": {
            filename: {
                "file_size": len(data),
                "processed_date": datetime_to_str(today()),
            }
            for filename, data in thies_fetched_files.items()
        },
    }
