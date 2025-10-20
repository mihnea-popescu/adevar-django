from datetime import (
    datetime,
    timedelta,
)


def get_local_time(utc_time: datetime, timezone_offset: int) -> datetime:
    """Convert UTC time to local time based on timezone offset

    Args:
        utc_time: The UTC datetime to convert
        timezone_offset: Minutes difference between local time and UTC.
            Negative values indicate ahead of UTC.
            For example, UTC+2 has offset -120 since local time minus 120 mins equals UTC.

    Returns:
        datetime: The local time after applying the timezone offset
    """
    return utc_time - timedelta(minutes=int(timezone_offset))