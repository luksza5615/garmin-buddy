import os
import zipfile
import pyodbc
import fitparse
import pandas as pd
from sqlalchemy import text
from datetime import datetime, timedelta
from garminconnect import Garmin
from dotenv import load_dotenv
from app.database.db_connector import SessionLocal
from app.utils.converter import convert_m_to_km, convert_seconds_to_time, convert_speed_to_pace
from app.services.garmin_connector import login_to_garmin

load_dotenv(override=True)

fit_dir_name = "fit_files"
fit_dir_path = os.getenv("FIT_DIR_PATH")
garmin_email = os.getenv("GARMIN_EMAIL")
garmin_password = os.getenv("GARMIN_PASSWORD")
fit_dir_path


def calculate_start_of_week(timestamp):
    week_start = timestamp - pd.to_timedelta(timestamp.weekday(), unit='D')
    return week_start

def datetime_to_id(dt):
    return int(dt.strftime("%Y%m%d%H%M%S"))

def check_if_activity_already_exists_in_db(checked_activity_timestamp):
    from app.services.db_service import get_activity_timestamps
    activities_rows_list = get_activity_timestamps()
    activities_timestamps_list = [
        row.activity_start_time for row in activities_rows_list]

    return checked_activity_timestamp in activities_timestamps_list


def set_download_start_date():
    # to avoid circular dependency
    from app.services.db_service import get_latest_activity_date
    latest_activity_date_in_db = get_latest_activity_date()

    files = [f for f in os.listdir(fit_dir_path) if os.path.isfile(
        os.path.join(fit_dir_path, f))]

    if not files:
        start_date = latest_activity_date_in_db
        print(f"No local FIT files found in '{fit_dir_path}'. Using last DB date: {start_date}")
        return start_date

    latest_file_name = sorted(files, reverse=True)[0]
    latest_file_date = datetime.strptime(
        latest_file_name[:10], "%Y-%m-%d").date()
    if latest_file_date > latest_activity_date_in_db:
        start_date = latest_file_date
    else:
        start_date = latest_activity_date_in_db

    print(f"Date of last saved activity: {start_date}")

    return start_date


def download_activities(refresh=True):

    garmin_connector = login_to_garmin(garmin_email, garmin_password)

    today = datetime.now().date()
    if refresh is True:
        start_date = set_download_start_date()
    else:
        # take activities up to 2000 days ao
        start_date = today - timedelta(days=2000)

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
            fit_dir_path, f"{activity_date}_{activity_type}_{activity_id}.zip")

        print(f"FIT_DIR_PATH: {fit_dir_path}")
        print(f"Saving ZIP to: {fit_path_zip}")

        try:
            with open(fit_path_zip, "wb") as f:
                f.write(fit_data)
        except Exception as e:
            print(f"Failed to save ZIP file '{fit_path_zip}': {e}")

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

            # Remove the zip file after extraction
            try:
                os.remove(fit_path_zip)
            except FileNotFoundError:
                pass

        except Exception as e:
            print(f"Failed to extract or remove ZIP '{fit_path_zip}': {e}")

    print(f"Files downloaded: {files}")
    print("Activities download finished")

    return files


def _list_existing_fit_files():
    files = []
    try:
        for f in os.listdir(fit_dir_path):
            full = os.path.join(fit_dir_path, f)
            if os.path.isfile(full) and f.lower().endswith('.fit'):
                files.append(full)
    except FileNotFoundError:
        pass
    return files


def _build_fit_filename(activity_date, activity_type, activity_id):
    return f"{activity_date}_{activity_type}_{activity_id}.fit"


def _build_zip_filename(activity_date, activity_type, activity_id):
    return f"{activity_date}_{activity_type}_{activity_id}.zip"


def _get_db_activity_timestamps_set():
    from app.services.db_service import get_activity_timestamps
    rows = get_activity_timestamps()
    return set([row.activity_start_time for row in rows])

def _get_db_activity_ids_set():
    from app.services.db_service import get_activity_ids
    rows = get_activity_ids()
    return set([row.activity_id for row in rows])


def _get_garmin_activities_full_history(garmin_connector, start_date=None, end_date=None, window_days=90):
    """
    Fetch activities across full history by paging through date windows.
    If start_date is None, default to a far past date.
    """
    if end_date is None:
        end_date = datetime.now().date()
    if start_date is None:
        start_date = datetime(1990, 1, 1).date()

    all_activities = []
    window_start = start_date
    while window_start <= end_date:
        window_end = min(window_start + timedelta(days=window_days), end_date)
        try:
            activities = garmin_connector.get_activities_by_date(
                window_start.isoformat(), window_end.isoformat())
            if activities:
                all_activities.extend(activities)
        except Exception as e:
            print(f"Failed to fetch activities for window {window_start} - {window_end}: {e}")
        window_start = window_end + timedelta(days=1)

    return all_activities


def sync_all_activities():
    """
    Full sync:
    1) Get set of activity timestamps from DB
    2) Get full activity list from Garmin (paged by date windows)
    3) For each Garmin activity:
       - If timestamp in DB: skip
       - Else, if corresponding .fit file exists: parse & save to DB
       - Else, download, extract .fit, parse & save
    Avoids duplicate downloads and ensures DB completeness.
    """
    
    garmin_connector = login_to_garmin(garmin_email, garmin_password)

    # db_timestamps = _get_db_activity_timestamps_set()
    db_ids = _get_db_activity_ids_set()
    # start_date = datetime(2023, 11, 24).date()
    # end_date = datetime(2023, 11, 24).date()
    garmin_activities = _get_garmin_activities_full_history(garmin_connector)
    existing_files = set(os.path.basename(p) for p in _list_existing_fit_files())

    processed = []

    for activity in garmin_activities:
        try:
            activity_id = activity['activityId']
            activity_type = activity['activityType']['typeKey']
            start_time = datetime.strptime(activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S")
            # print(f"Start time z biblioteki: {start_time}")
            activity_date = start_time.date()
            # activity_start_temp = activity['startTimeLocal']
            # print(f"TYP: {type(activity_start_temp)}")
            activity_db_id = datetime_to_id(start_time)

            if activity_db_id in db_ids:
                print("Activity already exists in DB")
                continue

            fit_filename = _build_fit_filename(activity_date, activity_type, activity_id)
            fit_filepath = os.path.join(fit_dir_path, fit_filename)

            if fit_filename in existing_files:
                # File already downloaded; parse and save to DB
                print("File already downloaded, but not saved in DB.")
                parse_and_save_file_to_db(fit_filepath)
                processed.append(fit_filepath)
                continue

            # Download from Garmin as ZIP, then extract to .fit
            fit_data = garmin_connector.download_activity(
                activity_id, dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL)

            zip_filename = _build_zip_filename(activity_date, activity_type, activity_id)
            fit_path_zip = os.path.join(fit_dir_path, zip_filename)

            try:
                with open(fit_path_zip, "wb") as f:
                    f.write(fit_data)
            except Exception as e:
                print(f"Failed to save ZIP file '{fit_path_zip}': {e}")
                continue

            try:
                with zipfile.ZipFile(fit_path_zip, 'r') as zip_ref:
                    for member in zip_ref.namelist():
                        new_filepath = fit_filepath
                        with zip_ref.open(member) as source, open(new_filepath, 'wb') as target:
                            target.write(source.read())
                try:
                    os.remove(fit_path_zip)
                except FileNotFoundError:
                    pass
            except Exception as e:
                print(f"Failed to extract or remove ZIP '{fit_path_zip}': {e}")
                continue

            # Parse and save to DB
            parse_and_save_file_to_db(fit_filepath)
            processed.append(fit_filepath)
        except Exception as e:
            print(f"Failed processing activity: {e}")

    print(f"Synced activities (files processed): {len(processed)}")
    return processed

def print_message_data(message_type, file_path):
    print(f"Message type: {message_type}")
    fitfile = fitparse.FitFile(file_path)

    records = fitfile.get_messages(message_type)

    if not records:
        print('No records in message type %s' % message_type)

    for record in records:
        for record_field in record:
            # Print the records name and value (and units if it has any)
            if record_field.units:
                print(" * %s: %s %s" % (
                    record_field.name, record_field.value, record_field.units,
                ))
            else:
                print(" * %s: %s" %
                      (record_field.name, record_field.value))

        print()


def parse_fit_file(file_path):
    print(f"Parsing {file_path}...")
    fitfile = fitparse.FitFile(file_path)

    message_types = ['activity', 'session']  # most important: session

    parsed_activity_data = {}
    for message_type in message_types:
        for record in fitfile.get_messages(message_type):
            for field in record:
                if field.name and field.value is not None:
                    parsed_activity_data[field.name] = field.value

            # print_message_data(message_type, file_path)

    print("FULLY PARSED ACTIVITY DATA: \n %s \n" % parsed_activity_data)

    return parsed_activity_data


def modify_subsport(sport, subsport):
    if sport == 'hiking':
        subsport = 'hiking'
    if sport == 'running' and subsport == 'generic':
        subsport = 'outdoor_running'

    return subsport


def calculate_efficiency_index(pace, avg_hr):
    # Expect "m:ss"; if missing/invalid, return None
    if not pace or ":" not in pace or avg_hr in (None, 0):
        return None
    minutes, seconds = pace.split(":")
    minutes = int(minutes)
    seconds = int(seconds)
    adjusted_pace = minutes + seconds / 60
    efficiency_index = round((100000 / (adjusted_pace * avg_hr)), 2)
    return efficiency_index


def prepare_activity_data_to_save_in_db(parsed_activity_data):
    activity_id = datetime_to_id(parsed_activity_data.get("start_time"))

    subsport = modify_subsport(parsed_activity_data.get(
        'sport'), parsed_activity_data.get("sub_sport"))

    grade_adjusted_avg_pace_min_per_km = convert_speed_to_pace(
        parsed_activity_data.get("enhanced_avg_speed"))

    if parsed_activity_data.get("sport") == "running":
        running_efficiency_index = calculate_efficiency_index(
            grade_adjusted_avg_pace_min_per_km, parsed_activity_data.get("avg_heart_rate"))
    else:
        running_efficiency_index = None

    activity_data_to_save_in_db = {
        "activity_id": activity_id,
        "activity_date": parsed_activity_data.get("local_timestamp"),
        "activity_start_time": parsed_activity_data.get("local_timestamp"),
        "sport": parsed_activity_data.get("sport"),
        "subsport": subsport,
        "distance_in_km": convert_m_to_km(parsed_activity_data.get("total_distance")),
        "elapsed_duration": convert_seconds_to_time(parsed_activity_data.get("total_elapsed_time")),
        "grade_adjusted_avg_pace_min_per_km": grade_adjusted_avg_pace_min_per_km,
        "avg_heart_rate": parsed_activity_data.get("avg_heart_rate"),
        "calories_burnt": parsed_activity_data.get("total_calories"),
        "aerobic_training_effect_0_to_5": parsed_activity_data.get("total_training_effect"),
        "anaerobic_training_effect_0_to_5": parsed_activity_data.get("total_anaerobic_training_effect"),
        "total_ascent_in_meters": parsed_activity_data.get("total_ascent"),
        "total_descent_in_meters": parsed_activity_data.get("total_descent"),
        "start_of_week": calculate_start_of_week(parsed_activity_data.get("timestamp")),
        "running_efficiency_index": running_efficiency_index
    }

    print(f"ACTIVITY DATA TO BE SAVED IN DB:\n {activity_data_to_save_in_db}")

    return activity_data_to_save_in_db


def save_activity_to_db(activity_data_to_save_in_db):
    if check_if_activity_already_exists_in_db(activity_data_to_save_in_db["activity_start_time"]) is False:
        try:
            query = text("""INSERT INTO activity (
                        activity_id, activity_date, activity_start_time, sport, subsport, distance_in_km, elapsed_duration, 
                        grade_adjusted_avg_pace_min_per_km, avg_heart_rate, calories_burnt, aerobic_training_effect_0_to_5, 
                        anaerobic_training_effect_0_to_5, total_ascent_in_meters, total_descent_in_meters, start_of_week, running_efficiency_index)
                    VALUES (
                        :activity_id, :activity_date, :activity_start_time, :sport, :subsport, :distance_in_km, :elapsed_duration,
                        :grade_adjusted_avg_pace_min_per_km, :avg_heart_rate, :calories_burnt,
                        :aerobic_training_effect_0_to_5, :anaerobic_training_effect_0_to_5,
                        :total_ascent_in_meters, :total_descent_in_meters, :start_of_week, :running_efficiency_index)
                    """)

            with SessionLocal() as session:
                conn = session.connection()
                conn.execute(query, activity_data_to_save_in_db)
                conn.commit()
            print("Activity %s_%s data saved in database sucessfully\n" % (
                activity_data_to_save_in_db["sport"], activity_data_to_save_in_db["activity_date"]))
        except pyodbc.ProgrammingError as e:
            print("Failed to save activity %s_%s due to error: %s" % (
                activity_data_to_save_in_db["sport"], activity_data_to_save_in_db["activity_date"], e))
    else:
        print("Activity %s already exists in the database\n" %
              (activity_data_to_save_in_db["activity_start_time"]))


def parse_and_save_file_to_db(fit_file_path):

    with open(fit_file_path, 'rb') as f:
        header_data = f.read(12)
        if header_data[8:12] == b'.FIT':
            activity_data_to_save_in_db = prepare_activity_data_to_save_in_db(
                parse_fit_file(fit_file_path))
            save_activity_to_db(
                activity_data_to_save_in_db)
        else:
            print(f"Invalid .fit file header: {fit_file_path}")


def review_fit_file_fields(file_path):
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
                      'device_info',
                      'device_settings',
                     'dive_alarm',
                     'dive_gas',
                     'dive_settings',
                     'dive_summary',
                     #  'event',
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
                     #  'lap',
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
                     #  'user_profile',s
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

    for message_type in message_types:
        print_message_data(message_type, file_path)


if __name__ == '__main__':
    # review_fit_file_fields('C:\\Users\\LSzata\\OneDrive - DXC Production\\Projects\\garmin\\fit-files\\2022-11-03_running_9911607177.fit')
    # sync_all_activities()
    sync_all_activities()
    # parse_fit_file('C:\\Users\\LSzata\\OneDrive - DXC Production\\Projects\\garmin\\fit-files\\2025-10-07_running_20618240154.fit')
    # fit_file_path_test = os.getenv("FIT_FILE_PATH_TEST")
    # parse_and_save_file_to_db(fit_file_path_test)
    # review_fit_file_fields(fit_file_path_test)
    # dt = datetime(2022, 11, 3, 18, 32, 51)
    # id_value = datetime_to_id(dt)
    # print(id_value)  
