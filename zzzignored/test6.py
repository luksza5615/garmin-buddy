

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


sp = convert_speed_to_pace(3.013)
print(sp)
