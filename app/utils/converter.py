def convert_speed_to_pace(speed_in_m_s):
    converted_speed = "-"

    if speed_in_m_s > 0:
        pace = (1000 / speed_in_m_s) / 60

        minutes = int(pace)
        seconds = round((pace - minutes) * 60)

        if seconds < 10:
            seconds = f"0{seconds}"

        converted_speed = f"{minutes}:{seconds}"

    return converted_speed


def convert_seconds_to_time(seconds):
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


def convert_m_to_km(value_in_m):
    value_in_km = value_in_m / 1000

    return f"{value_in_km:.2f}"
