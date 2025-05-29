import fitparse
import sqlite3
from datetime import datetime
from garminconnect import Garmin

db_path = "C:\\Users\\SzataLukasz\\Documents\\Dysk Google\\Projects\\garmin-my\\garmin_data.db"
db_path = "C:\\Users\\SzataLukasz\\HealthData\\DBs\\garmin.db"
fit_file = "C:\\Users\\SzataLukasz\\Desktop\\18065439090_ACTIVITY.fit"

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


# Example dictionary with the date-time string
activity_data = {'startTimeLocal': '2025-02-16 14:58:03'}

# Convert string to datetime object
dt_object = datetime.strptime(
    activity_data['startTimeLocal'], "%Y-%m-%d %H:%M:%S")

# Extract only the date part
date_only = dt_object.date()

print(date_only)


def convert_seconds_to_time(seconds):
    hours = int(seconds // 3600)
    if hours < 10:
        hours = f"0{hours}"
    print(f"Hours: {hours}\n")
    minutes = int((seconds % 3600) // 60)
    if minutes < 10:
        minutes = f"0{minutes}"
    print(f"Minutes: {minutes}\n")
    seconds = int(round((seconds % 60), 0))
    if seconds < 10:
        seconds = f"0{seconds}"
    print(f"Seconds: {seconds}\n")

    return f"{hours}:{minutes}:{seconds}"


print(convert_seconds_to_time(1922.887))


def convert_speed_to_pace(speed_in_m_s):
    pace = (1000 / speed_in_m_s) / 60

    minutes = int(pace)
    seconds = round((pace - minutes) * 60)

    if seconds < 10:
        seconds = f"0{seconds}"

    return f"{minutes}:{seconds}"


def login_to_garmin_connect(email, password):
    try:
        garmin_connector = Garmin(email, password)
        garmin_connector.login()
        print("Logged successfully")
    except Exception as e:
        print(f"Failed to login: {e}")

    return garmin_connector


def download_activities_without_saving(garmin_connector):
    activities = garmin_connector.get_activities(1, 2)

    for activity in activities:
        activity_id = activity["activityId"]
        print('Activity basic data: ')
        print(activity)
        print("\n")
        data_to_save = {
            "activity_id": activity["activityId"],
            "activity_name": activity["activityName"],
            "begin_timestamp": activity["beginTimestamp"],
            "distance": activity["distance"],
            "duration": activity["elapsedDuration"],
            "average_speed": activity["averageSpeed"],
            "calories": activity["calories"],
            "average_hr": activity["averageHR"],
            "aerobic_training_effect": activity["aerobicTrainingEffect"],
            "aerobic_training_effect_message": activity["aerobicTrainingEffectMessage"],
            "anaerobic_training_effect_message": activity["anaerobicTrainingEffectMessage"],
            "anaerobic_training_effect": activity["anaerobicTrainingEffect"],
            "training_benefit": activity["trainingEffectLabel"],
            "trainig_load": activity["trainingLoad"],
            "difference_body_battery": activity["differenceBodyBattery"],
            "hr_timezone_1": activity["hrTimeInZone_1"],
            "hr_timezone_2": activity["hrTimeInZone_2"],
            "hr_timezone_3": activity["hrTimeInZone_3"],
            "hr_timezone_4": activity["hrTimeInZone_4"],
            "hr_timezone_5": activity["hrTimeInZone_5"],
            "avg_respiration_rate": activity["avgRespirationRate"],

        }
        print(
            f"Activity detailed data {garmin_connector.get_activity(activity_id)}\n")

        print(
            f"Activity hr data {garmin_connector.get_activity_hr_in_timezones(activity_id)}\n")
        print(
            f"Activity splits: {garmin_connector.get_activity_splits(activity_id)} \n")
        print(
            f"Activity split sumamries: {garmin_connector.get_activity_split_summaries(activity_id)}\n")
        garmin_connector.get_activity_laps(activity_id)

    return data_to_save


def save_activity_to_db(data_to_save_in_db, connection):
    try:
        connection.execute(
            """
            INSERT INTO activity_data (position_lat, position_long, altitude, distance, speed, heart_rate)
            VALUES (:position_lat, :position_long, :altitude, :distance, :speed, :heart_rate)
            """
        )
        print("Data inserted sucessfully")
    except pyodbc.ProgrammingError as e:
        print(f"Failed to insert data: {e}")


def create_sqlite_table(sqlite_cursor):
    sqlite_cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            position_lat REAL,
            position_long REAL,
            altitude REAL,
            distance REAL,
            speed REAL,
            heart_rate INTEGER
            )
    """)


# Function to parse FIT files
# def parse_fit_file(file_path):
#     print(f"Processing {file_path}...")
#     fitfile = fitparse.FitFile(file_path)

#     # Iterate over messages in the file
#     for record in fitfile.get_messages("record"):  # "record" contains activity data points
#         data = {}
#         for field in record:
#             if field.name and field.value is not None:
#                 data[field.name] = field.value
#         print(data)  # Print each record's data (or save it)
#     print(f"Completed processing {file_path}.\n")

# Iterate over all FIT files in the directory
# for file_name in os.listdir(fit_directory):
#     if file_name.endswith(".fit"):
#         file_path = os.path.join(fit_directory, file_name)
#         parse_fit_file(file_path)


# parse_fit_file(fit_file)


def save_to_db(data):
    cursor.execute("""
        INSERT INTO activity_data (timestamp, position_lat, position_long, altitude, distance, speed, heart_rate)
        VALUES (:timestamp, :position_lat, :position_long, :altitude, :distance, :speed, :heart_rate)
    """, data)
    conn.commit()


def parse_fit_file_to_db(file_path):
    print(f"Processing {file_path}...")
    fitfile = fitparse.FitFile(file_path)
    for record in fitfile.get_messages("record"):
        data = {}
        for field in record:
            if field.name and field.value is not None:
                data[field.name] = field.value

        # Simplify data keys to match the database schema
        db_data = {
            "timestamp": data.get("timestamp"),
            "position_lat": data.get("position_lat"),
            "position_long": data.get("position_long"),
            "altitude": data.get("altitude"),
            "distance": data.get("distance"),
            "speed": data.get("speed"),
            "heart_rate": data.get("heart_rate"),
        }
        save_to_db(db_data)
    print(f"Completed processing {file_path}.\n")


def parse_single_fit_file_without_saving(fit_file_path):
    with open(fit_file_path, 'rb') as f:
        header_data = f.read(12)
        if header_data[8:12] == b'.FIT':
            # print(f'file_path : {fit_file_path}')
            parse_fit_file(fit_file_path)
            # print(f'File {file_path} saved to db')
        else:
            print(f"Invalid .fit file header: {fit_file_path}")


cursor.execute("""
CREATE TABLE IF NOT EXISTS activity_data (
    timestamp TEXT,
    position_lat REAL,
    position_long REAL,
    altitude REAL,
    distance REAL,
    speed REAL,
    heart_rate INTEGER
)
""")

parse_fit_file_to_db(fit_file)


# sqlite_connection = sqlite3.connect(db_path)
# sqlite_cursor = sqlite_connection.cursor()

# parse_and_save_all_files_to_db(fit_dir_path, sqlite_connection)
# sqlite_connection.commit()
