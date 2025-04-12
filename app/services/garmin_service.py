import os
import zipfile
import pyodbc
import fitparse
from fitfile import FitFile as TestFitFile
from numpy import empty
from sqlalchemy import text
from datetime import datetime, timedelta
from garminconnect import Garmin
from dotenv import load_dotenv
from app.database.db_connector import SessionLocal
from app.utils.converter import convert_m_to_km, convert_seconds_to_time, convert_speed_to_pace
from app.services.garmin_connector import login_to_garmin

load_dotenv(override=True)

fit_dir_path = os.getenv("FIT_DIR_PATH")
garmin_email = os.getenv("GARMIN_EMAIL")
garmin_password = os.getenv("GARMIN_PASSWORD")


def download_activities(refresh=True):
    from app.services.db_service import get_latest_activity_date
    garmin_connector = login_to_garmin(garmin_email, garmin_password)
    fit_dir_name = "fit_files"
    today = datetime.now().date()

    if refresh is True:
        latest_activity_date_in_db = get_latest_activity_date()

        files = [f for f in os.listdir(fit_dir_path) if os.path.isfile(
            os.path.join(fit_dir_path, f))]
        latest_file_name = sorted(files, reverse=True)[0]
        latest_file_date = datetime.strptime(
            latest_file_name[:10], "%Y-%m-%d").date()
        if latest_file_date > latest_activity_date_in_db:
            start_date = latest_file_date
        else:
            start_date = latest_activity_date_in_db
    else:
        start_date = today - timedelta(days=2000)

    print(f"Last activity date in database: {start_date}\n")

    activities = garmin_connector.get_activities_by_date(
        start_date.isoformat(), today.isoformat())

    files = []

    for activity in activities:
        activity_id = activity['activityId']
        activity_type = activity['activityType']['typeKey']
        start_time = datetime.strptime(
            activity['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
        activity_date = start_time.date()

        fit_data = garmin_connector.download_activity(
            activity_id, dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL)

        fit_path_zip = os.path.join(
            fit_dir_name, f"{activity_date}_{activity_type}_{activity_id}.zip")

        try:
            with open(fit_path_zip, "wb") as f:
                f.write(fit_data)
        except Exception as e:
            print(f"Failed to save: {e}")

        try:
            with zipfile.ZipFile(fit_path_zip, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    # Customize the name for each extracted file

                    new_filename = f"{activity_date}_{activity_type}_{activity_id}.fit"
                    new_filepath = os.path.join(fit_dir_path, new_filename)

                    # Extract and rename the file
                    with zip_ref.open(member) as source, open(new_filepath, 'wb') as target:
                        target.write(source.read())

                    files.append(new_filepath)
                print(f"Files downloaded: {files}")

            # Remove the zip file after extraction
            os.remove(fit_path_zip)

        except Exception as e:
            print(f"Failed to extract or remove zip file: {e}")

    print("Activities download finished\n")

    return files


def modify_subsport(sport, subsport):
    if sport == 'hiking':
        subsport = 'hiking'
    if sport == 'running' and subsport == 'generic':
        subsport = 'outdoor_running'

    return subsport


def parse_fit_file(file_path):
    # print(f"Processing {file_path}...")
    fitfile = fitparse.FitFile(file_path)

    # message_types = ['activity', 'session',
    #  'hr_zones_time']  # most important: session

    message_types = ['accelerometer_data',
                     'activity',
                     'ant_channel_id',
                     'ant_rx',
                     'ant_tx',
                     'aviation_attitude',
                     'barometer_data',
                     'bike_profile',
                     'blood_pressure',
                     'cadence_zone',
                     'camera_event',
                     'capabilities',
                     'connectivity',
                     'course',
                     'course_point',
                     #  'device_info',
                     'device_settings',
                     'dive_alarm',
                     'dive_gas',
                     'dive_settings',
                     'dive_summary',
                     'event',
                     'exd_data_concept_configuration',
                     'exd_data_field_configuration',
                     'exd_screen_configuration',
                     'exercise_title',
                     'field_capabilities',
                     'file_capabilities',
                     'file_creator',
                     'goal',
                     #  'gps_metadata',
                     'gyroscope_data',
                     'hr',
                     'hr_zone',
                     'hrm_profile',
                     'lap',
                     'length',
                     'magnetometer_data',
                     'memo_glob',
                     'mesg_capabilities',
                     'met_zone',
                     'monitoring',
                     'monitoring_info',
                     'nmea_sentence',
                     'obdii_data',
                     'ohr_settings',
                     'one_d_sensor_calibration',
                     'power_zone',
                     #  'record',
                     'schedule',
                     'sdm_profile',
                     'segment_lap',
                     'session',
                     'set',
                     'slave_device',
                     'software',
                     'speed_zone',
                     'sport',
                     'three_d_sensor_calibration',
                     'timestamp_correlation',
                     'totals',
                     'user_profile',
                     'video',
                     'video_clip',
                     'video_description',
                     'video_frame',
                     'video_title',
                     'watchface_settings',
                     'weather_alert',
                     'weather_conditions',
                     'weight_scale',
                     'workout',
                     'workout_session',
                     'workout_step',
                     'zones_target']

    # hr_zone_times = {}

    # Look for session messages which often include HR zone times
    # for msg in fitfile.get_messages("hr_zone"):
    #     data = msg.get_values()

    #     # Garmin often stores hr_zone_times as a list or repeated fields
    #     if "hr_zone_high_bpm" in data and "name" in data:
    #         # e.g. [116, 133, 150, 167, 184]
    #         zone_highs = data["hr_zone_high_bpm"]
    #         # e.g. [120, 230, 600, 900, 50] (in seconds)
    #         zone_times = data["name"]

    #         for i, seconds in enumerate(zone_times):
    #             hr_zone_times[f"hrz_{i+1}_time"] = timedelta(seconds=seconds)
    #         break  # Usually only one session message needed

    # print("STREFY: ")
    # print(hr_zone_times)

    for message_type in message_types:
        i = 0
        for record in fitfile.get_messages(message_type):
            data = {}
            for field in record:
                if field.name and field.value is not None:
                    data[field.name] = field.value

            # list of fields in message type
            print(f"Message type: {message_type}")
            # Go through all the data entries in this record
            for record_data in record:

                # Print the records name and value (and units if it has any)
                if record_data.units:
                    print(" * %s: %s %s" % (
                        record_data.name, record_data.value, record_data.units,
                    ))
                else:
                    print(" * %s: %s" % (record_data.name, record_data.value))

            print()
            i = i+1
        print(f"Record {i} processed\n")

    subsport = modify_subsport(data.get('sport'), data.get("sub_sport"))

    data_to_save_in_db = {
        "activity_date": data.get("timestamp"),
        "activity_start_time": data.get("timestamp"),
        "sport": data.get("sport"),
        "subsport": subsport,
        "distance_in_km": convert_m_to_km(data.get("total_distance")),
        "elapsed_duration": convert_seconds_to_time(data.get("total_elapsed_time")),
        "grade_adjusted_avg_pace_min_per_km": convert_speed_to_pace(data.get("enhanced_avg_speed")),
        "avg_heart_rate": data.get("avg_heart_rate"),
        "calories_burnt": data.get("total_calories"),
        "aerobic_training_effect_0_to_5": data.get("total_training_effect"),
        "anaerobic_training_effect_0_to_5": data.get("total_anaerobic_training_effect"),
        "total_ascent_in_meters": data.get("total_ascent"),
        "total_descent_in_meters": data.get("total_descent"),
    }

    print(data_to_save_in_db)

    return data_to_save_in_db


def debug_session_fields(filepath):
    fitfile = FitFile(filepath)
    for msg in fitfile.get_messages("session"):
        print("SESSION MESSAGE:")
        for record in msg:
            print(f"{record.name}: {record.value}")


def save_activity_to_db(data_to_save_in_db):
    try:
        query = text("""INSERT INTO activity_data (
                    activity_date, activity_start_time, sport, subsport, distance_in_km, elapsed_duration, 
                    grade_adjusted_avg_pace_min_per_km, avg_heart_rate, calories_burnt, aerobic_training_effect_0_to_5, 
                    anaerobic_training_effect_0_to_5, total_ascent_in_meters, total_descent_in_meters)
                VALUES (
                    :activity_date, :activity_start_time, :sport, :subsport, :distance_in_km, :elapsed_duration,
                    :grade_adjusted_avg_pace_min_per_km, :avg_heart_rate, :calories_burnt,
                    :aerobic_training_effect_0_to_5, :anaerobic_training_effect_0_to_5,
                    :total_ascent_in_meters, :total_descent_in_meters)
                """)

        with SessionLocal() as session:
            conn = session.connection()
            conn.execute(query, data_to_save_in_db)
            conn.commit()
        print("Data saved in database sucessfully")
    except pyodbc.ProgrammingError as e:
        print(f"Failed to save data: {e}")


def parse_and_save_single_file_to_db(fit_file_path):

    with open(fit_file_path, 'rb') as f:
        header_data = f.read(12)
        if header_data[8:12] == b'.FIT':
            print(f'file_path : {fit_file_path}')
            save_activity_to_db(
                parse_fit_file(fit_file_path))
            print(f'File {fit_file_path} saved to db')
        else:
            print(f"Invalid .fit file header: {fit_file_path}")


def parse_and_save_all_files_to_db(fit_directory_path, db_connection, files=[], refresh=True):
    if refresh is True:
        fit_files = files
    else:
        print("czytam fit files")
        fit_files = [file for file in os.listdir(
            fit_directory_path) if file.endswith(".fit")]

    if fit_files is empty:
        print('Directory is empty')
        return

    if fit_files is not empty:
        for f in fit_files:
            file_path = os.path.join(fit_directory_path, f)
            with open(file_path, 'rb') as f:
                header_data = f.read(12)
                if header_data[8:12] == b'.FIT':
                    print(f'file_path : {file_path}')
                    save_activity_to_db(
                        parse_fit_file(file_path))
                    print(f'File {file_path} saved to db')
                else:
                    print(f"Invalid .fit file header: {file_path}")


if __name__ == '__main__':
    fit_file_path_test = os.getenv("FIT_FILE_PATH_TEST")
    parse_fit_file(fit_file_path_test)
    # debug_session_fields(fit_file_path_test)
