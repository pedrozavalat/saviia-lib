from typing import Any

from rcer_iot_client_pkg.libs.zero_dependency.utils.datetime_utils import (
    datetime_to_str,
    today,
)


def parse_execute_response(
    file_contents: dict[str, Any],
) -> dict[str, dict[str, int | str]]:
    return {
        filename: {
            "size": len(data),
            "date": datetime_to_str(today()),
        }
        for filename, data in file_contents.items()
    }
