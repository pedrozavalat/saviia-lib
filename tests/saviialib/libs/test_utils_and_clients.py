from datetime import datetime
from unittest.mock import MagicMock

import pytest

from saviialib.general_types.error_types.api.saviia_api_error_types import ValidationError
from saviialib.libs.directory_client.client.os_client import OsClient
from saviialib.libs.log_client.logging_client.logging_client import LoggingClient
from saviialib.libs.log_client.types.log_client_types import DebugArgs, ErrorArgs, InfoArgs, LogClientArgs, LogStatus, WarningArgs
from saviialib.libs.log_client.utils.log_client_utils import format_message
from saviialib.libs.schema_validator_client.clients.jsonschema.jsonschema_client import JsonschemaClient
from saviialib.libs.zero_dependency.utils.booleans_utils import boolean_to_emoji
from saviialib.libs.zero_dependency.utils.datetime_utils import (
    datetime_to_str,
    datetime_to_timestamp,
    difference,
    is_within_date_range,
    str_to_datetime,
    str_to_timestamp,
)
from saviialib.libs.zero_dependency.utils.strings_utils import are_equal


def test_should_map_boolean_to_emoji():
    assert boolean_to_emoji(True) == "✅"
    assert boolean_to_emoji(False) == "❌"


def test_should_compare_strings_case_insensitively():
    assert are_equal("HELLO", "hello") is True
    assert are_equal("HELLO", "world") is False


def test_should_convert_datetime_formats_and_timestamps():
    dt = datetime(2025, 1, 2, 3, 4, 5)

    as_str = datetime_to_str(dt, "%Y-%m-%d")
    as_dt = str_to_datetime("2025-01-02", "%Y-%m-%d")
    as_ts = str_to_timestamp("2025-01-02", "%Y-%m-%d")

    assert as_str == "2025-01-02"
    assert as_dt == datetime(2025, 1, 2)
    assert isinstance(as_ts, float)
    assert isinstance(datetime_to_timestamp(dt, "%Y-%m-%d %H:%M:%S"), float)


def test_should_validate_date_range_and_difference():
    target = "01/02/2025, 00:00:00"
    target_ts = str_to_timestamp(target)

    assert is_within_date_range(target, after=target_ts - 10, before=target_ts + 10)
    assert not is_within_date_range(target, after=target_ts + 1)
    assert not is_within_date_range(target, before=target_ts - 1)
    assert difference(datetime(2025, 1, 10), 2) == datetime(2025, 1, 8)


def test_should_format_log_message():
    assert format_message("A", "b", LogStatus.STARTED) == "A::b_started"
    assert format_message("A", "b", LogStatus.ERROR, "boom") == "A::b_error: boom"


def test_should_validate_jsonschema_client_and_format_errors():
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string", "maxLength": 3}, "tags": {"type": "array", "maxItems": 1}},
        "required": ["name"],
        "additionalProperties": False,
    }
    client = JsonschemaClient(schema)

    assert client.validate({"name": "abc", "tags": ["x"]}) is True
    with pytest.raises(ValidationError):
        client.validate({"name": "abcd"})
    with pytest.raises(ValidationError):
        client.validate({"name": "ab", "tags": ["x", "y"]})


@pytest.mark.asyncio
async def test_should_operate_os_client_filesystem(tmp_path):
    root = tmp_path / "root"
    child = root / "child"
    file_path = child / "f.txt"

    await OsClient.makedirs(str(child))
    await OsClient.touch(str(file_path))
    assert await OsClient.path_exists(str(file_path))
    assert await OsClient.isdir(str(child))

    listing = await OsClient.listdir(str(child))
    listing_info = await OsClient.listdir(str(child), more_info=True)
    assert "f.txt" in listing
    assert any(name == "f.txt" for name, _ in listing_info)

    assert OsClient.relative_path(str(file_path), str(root)) == "child/f.txt"
    assert OsClient.get_basename(str(file_path)) == "f.txt"

    await OsClient.remove_file(str(file_path))
    assert not await OsClient.path_exists(str(file_path))

    await OsClient.removedirs(str(root))
    assert not await OsClient.path_exists(str(root))


def test_should_record_and_dispatch_logs_when_active_record_enabled():
    logger = MagicMock()
    client = LoggingClient(
        LogClientArgs(class_name="klass", method_name="exec", active_record=True, logger=logger)
    )

    client.info(InfoArgs(LogStatus.STARTED, {"msg": "i"}))
    client.debug(DebugArgs(LogStatus.SUCCESSFUL, {"msg": "d"}))
    client.warning(WarningArgs(LogStatus.ALERT, {"msg": "w"}))
    client.error(ErrorArgs(LogStatus.ERROR, {"msg": "e"}))

    assert len(client.log_history) == 4
    logger.info.assert_called_once()
    logger.debug.assert_called_once()
    logger.warning.assert_called_once()
    logger.error.assert_called_once()
