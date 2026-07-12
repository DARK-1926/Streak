import datetime
from zoneinfo import ZoneInfo

def get_current_utc_time() -> datetime.datetime:
    """
    Get the current UTC time.

    Returns:
        datetime.datetime: The current UTC time.
    """
    try:
        return datetime.datetime.now(datetime.timezone.utc)
    except Exception as e:
        print(f"An error occurred while getting the current UTC time: {e}")
        raise

def convert_to_utc(timestamp: datetime.datetime, timezone: str) -> datetime.datetime:
    """
    Convert a given timestamp from a specified timezone to UTC.

    Args:
        timestamp (datetime.datetime): The timestamp to convert.
        timezone (str): The timezone of the given timestamp (e.g., 'America/New_York').

    Returns:
        datetime.datetime: The converted timestamp in UTC.
    """
    local_tz = ZoneInfo(timezone)
    local_dt = timestamp.replace(tzinfo=local_tz)
    utc_dt = local_dt.astimezone(ZoneInfo('UTC'))
    return utc_dt
