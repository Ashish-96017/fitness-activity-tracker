from __future__ import annotations

from datetime import datetime

ALLOWED_ACTIVITIES = {"Walking", "Running", "Cycling"}


def validate_date(value: str) -> str:
    value = value.strip()
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Date must be in YYYY-MM-DD format.") from exc
    return parsed.strftime("%Y-%m-%d")


def validate_activity_type(value: str) -> str:
    normalized = value.strip().title()
    if normalized not in ALLOWED_ACTIVITIES:
        raise ValueError("Activity type must be Walking, Running, or Cycling.")
    return normalized


def validate_positive_number(value: str, field_name: str, max_value: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number.") from exc
    if number <= 0:
        raise ValueError(f"{field_name} must be greater than 0.")
    if number > max_value:
        raise ValueError(f"{field_name} must be at most {max_value:g}.")
    return number


def validate_activity(date: str, activity_type: str, duration: str, distance: str) -> tuple[str, str, float, float]:
    clean_date = validate_date(date)
    clean_type = validate_activity_type(activity_type)
    clean_duration = validate_positive_number(duration, "Duration", 1440)
    clean_distance = validate_positive_number(distance, "Distance", 1000)
    return clean_date, clean_type, clean_duration, clean_distance
