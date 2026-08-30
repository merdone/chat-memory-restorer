from datetime import datetime
import random
import string

DATE_FORMAT = "%Y:%m:%d %H:%M:%S%z"


def formate_date_for_windows(date):
    return datetime.strftime(date, DATE_FORMAT)


def formate_date_to_iso(date):
    return date.isoformat()


def string_to_datetime(date_string: str) -> datetime | None:
    if date_string is None:
        return None

    if date_string.startswith("0000"):
        return None

    try:
        normalized = date_string[:10].replace(":", "-") + date_string[10:]
        return datetime.fromisoformat(normalized)
    except (ValueError, TypeError):
        return None


async def generate_file_name(date) -> str:
    random_part = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10))
    return date.strftime('%d_%m_%Y_') + random_part


def convert_timezones(date_dict):
    timezone = get_timezone(date_dict)

    for key, date in date_dict.items():
        if date_dict[key] is not None:
            date_dict[key] = date.astimezone(timezone)


def get_timezone(date_dict):
    timezone = None
    for date in date_dict.values():
        if date is not None:
            if date.tzinfo:
                timezone = date.tzinfo
                break
    return timezone


def get_min_date(date_dict, current_min_date):
    min_date = current_min_date.astimezone(get_timezone(date_dict))
    for current_date in date_dict.values():
        if current_date is not None:
            if current_date < min_date:
                min_date = current_date
    return min_date
