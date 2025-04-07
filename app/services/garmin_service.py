import os
import zipfile
import pyodbc
import fitparse
from numpy import empty
from sqlalchemy import text
from datetime import datetime, timedelta
from garminconnect import Garmin
from dotenv import load_dotenv
from app.database.db_connector import SessionLocal
from app.utils.converter import convert_m_to_km, convert_seconds_to_time, convert_speed_to_pace
from app.services.garmin_connector import login_to_garmin


load_dotenv(override=True)

fit_dir_name = "fit_files"
fit_file_path_test = os.getenv("FIT_FILE_PATH_TEST")
fit_dir_path = os.getenv("FIT_DIR_PATH")
garmin_email = os.getenv("GARMIN_EMAIL")
garmin_password = os.getenv("GARMIN_PASSWORD")


def download_activities(db_connection, refresh=True):
    from app.services.db_service import get_latest_activity_date
    garmin_connector = login_to_garmin(garmin_email, garmin_password)
    os.makedirs(fit_dir_name, exist_ok=True)

    today = datetime.now().date()

    if refresh is True:
        start_date = get_latest_activity_date()
    else:
        start_date = today - timedelta(days=2000)

    print(f"Start date: {start_date}\n")

    # activities = garmin_connector.get_activities(0, 2) # get_activities(start, limit) starting from latest
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
            print("File saved")
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

                    print(f"new_filepath: {new_filepath}")
                    files.append(new_filepath)
                    print(f"Files: {files}")
            print(f"Extracted to: {fit_dir_path}")

            # Remove the zip file after extraction
            os.remove(fit_path_zip)
            print(f"Removed zip file: {fit_path_zip}")
        except Exception as e:
            print(f"Failed to extract or remove zip file: {e}")

    print("Method download_activities executed\n")

    return files


def parse_fit_file(file_path):
    # print(f"Processing {file_path}...")
    fitfile = fitparse.FitFile(file_path)

    message_types = ['activity', 'session']  # most important: session

    for message_type in message_types:
        # i = 0
        for record in fitfile.get_messages(message_type):
            data = {}
            for field in record:
                if field.name and field.value is not None:
                    data[field.name] = field.value

            # list of fields in message type
        #     print(f"Message type: {message_type}")
        #     # Go through all the data entries in this record
        #     for record_data in record:

        #         # Print the records name and value (and units if it has any)
        #         if record_data.units:
        #             print(" * %s: %s %s" % (
        #                 record_data.name, record_data.value, record_data.units,
        #             ))
        #         else:
        #             print(" * %s: %s" % (record_data.name, record_data.value))

        #     print()
        #     i = i+1
        # print(f"Record {i} processed\n")

    data_to_save_in_db = {
        "sport": data.get("sport"),
        "subsport": data.get("sub_sport"),
        "timestamp": data.get("timestamp"),
        "distance": convert_m_to_km(data.get("total_distance")),
        "elapsed_time": convert_seconds_to_time(data.get("total_elapsed_time")),
        "enhanced_avg_pace": convert_speed_to_pace(data.get("enhanced_avg_speed")),
        "avg_heart_rate": data.get("avg_heart_rate"),
        # TODO: not sure if that is aerobic
        "calories": data.get("total_calories"),
        "aerobic_training_effect": data.get("total_training_effect"),
        "anaerobic_training_effect": data.get("total_anaerobic_training_effect"),
        "total_ascent": data.get("total_ascent"),
        "total_descent": data.get("total_descent"),
    }

    print(data_to_save_in_db)

    return data_to_save_in_db


def save_activity_to_db(data_to_save_in_db, db_connection):
    try:
        query = text("""INSERT INTO activity_data (
                    sport, subsport, timestamp, distance_km, elapsed_time, 
                    enhanced_avg_pace, avg_heart_rate, calories, aerobic_training_effect, 
                    anaerobic_training_effect, total_ascent, total_descent)
                VALUES (
                    :sport, :subsport, :timestamp, :distance, :elapsed_time,
                    :enhanced_avg_pace, :avg_heart_rate, :calories,
                    :aerobic_training_effect, :anaerobic_training_effect,
                    :total_ascent, :total_descent)
                """)

        with SessionLocal() as session:
            conn = session.connection()
            conn.execute(query, data_to_save_in_db)
            conn.commit()
        print("Data inserted sucessfully")
    except pyodbc.ProgrammingError as e:
        print(f"Failed to insert data: {e}")


def parse_and_save_single_file_to_db(fit_file_path, db_connection):

    with open(fit_file_path, 'rb') as f:
        header_data = f.read(12)
        if header_data[8:12] == b'.FIT':
            print(f'file_path : {fit_file_path}')
            save_activity_to_db(
                parse_fit_file(fit_file_path), db_connection)
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
                        parse_fit_file(file_path), db_connection)
                    print(f'File {file_path} saved to db')
                else:
                    print(f"Invalid .fit file header: {file_path}")
