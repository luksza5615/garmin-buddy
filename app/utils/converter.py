from numpy.ma.core import round_
import pandas as pd

def calculate_start_of_week(timestamp):
    week_start = timestamp - pd.to_timedelta(timestamp.weekday(), unit="D")
    return week_start


def convert_speed_to_pace(speed_in_m_s):
    # converted_speed = "-"

    if speed_in_m_s is None:
        return None

    try:
        if speed_in_m_s > 0:
            pace = (1000 / speed_in_m_s) / 60

            minutes = int(pace)
            seconds = round((pace - minutes) * 60)

            # Normalize rounding to 60 sec edge case
            if seconds == 60:
                minutes += 1
                seconds = 0

            if seconds < 10:
                seconds = f"0{seconds}"

            converted_speed = f"{minutes}:{seconds}"
    except Exception:
        # keep default "-"
        return None

    return converted_speed


def convert_seconds_to_time(seconds):
    if seconds is None:
        return None

    try:
        hours = int(seconds // 3600)
        if hours < 10:
            hours = f"0{hours}"

        minutes = int((seconds % 3600) // 60)
        if minutes < 10:
            minutes = f"0{minutes}"

        seconds = int(round((seconds % 60), 0))
        if seconds < 10:
            seconds = f"0{seconds}"

        return f"{hours}:{minutes}:{seconds}"
    except Exception:
        return None

def convert_m_to_km(value_in_m: float | None) -> float:
    if value_in_m is None:
        return None

    try:
        value_in_km = value_in_m / 1000
        return round(value_in_km, 2)
    except Exception:
        return None

