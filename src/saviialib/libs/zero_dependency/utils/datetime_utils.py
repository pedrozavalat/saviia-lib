from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo


def today(timezone: str = "America/Santiago") -> datetime:
    """
    Return the current date.

    :param timezone: A string representing the IANA timezone name.
        Defaults to "America/Santiago".
    :return datetime:
    """
    return datetime.now(tz=ZoneInfo(timezone))


def datetime_to_str(date: datetime, date_format: str = "%m/%d/%Y, %H:%M:%S") -> str:
    """
    Convert a datetime object to a string in the specified format.

    :param date: The datetime object to convert.
    :param date_format: The format to convert the datetime object to.
        Defaults to "%Y-%m-%dT%H:%M:%S".
    :return: A string in the specified format.
    """
    return date.strftime(date_format)


def datetime_to_timestamp(date: datetime, date_format: str = "%m/%d/%Y, %H:%M:%S") -> float:
    return str_to_timestamp(datetime_to_str(date, date_format), date_format)

def str_to_datetime(date: str, date_format: str = "%m/%d/%Y, %H:%M:%S") -> datetime:
    """
    Convert a string to a datetime object in the specified format.

    :param date: The string to convert.
    :param date_format: The format of the string.
        Defaults to "%Y-%m-%dT%H:%M:%S".
    :return: A datetime object.
    """
    return datetime.strptime(date, date_format)


def str_to_timestamp(
    date: str,
    date_format: str = "%m/%d/%Y, %H:%M:%S",
    timezone: str = "America/Santiago",
) -> float:
    """
    Docstring para str_to_timestamp

    :param date: Datetime in YYYY-MM-DD format
    :type date: str
    :param date_format: yyyy-mm-dd by default
    :type date_format: str
    :param timezone: America/Santiago by default
    :type timezone: str
    :return: Datetime timestamp
    :rtype: float
    """
    return datetime.strptime(date, date_format).timestamp()


def is_within_date_range(
    date: str, after: Optional[int] = None, before: Optional[int] = None
) -> bool:
    date_ts = str_to_timestamp(date)
    if after and date_ts < after:
        return False
    if before and date_ts > before:
        return False
    return True


def difference(date: datetime, n: int) -> datetime:
    return date - timedelta(days=n)
