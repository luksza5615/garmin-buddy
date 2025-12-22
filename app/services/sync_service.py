import logging
from app.config import Config
from app.services.garmin_connector import login_to_garmin
from app.services.db_service import Database
from app.services.garmin_client import GarminClient
from app.services.fitfile_service  import FitFileStore
from app.services.activity_service import ActivityMapper
from app.services.db_service import ActivityRepository
from app.utils.converter import datetime_to_id
import os
import zipfile
import logging
from sqlalchemy import text
from datetime import datetime, timedelta
from garminconnect import Garmin
from app.services.garmin_connector import login_to_garmin
from app.config import Config
from app.database.db_connector import Database

logger = logging.getLogger(__name__)

class SyncService():
    def __init__(self):
        pass

    def sync_activities(self, configuration: Config, database: Database):
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
        garmin_connector = login_to_garmin(configuration.garmin_email, configuration.garmin_password)
        filestore = FitFileStore()
        garmin_client = GarminClient()
        activity_mapper = ActivityMapper()
        activity_repository = ActivityRepository()

        db_ids = activity_repository.get_db_activity_ids_set(database)
        garmin_activities = garmin_client.get_garmin_activities_full_history(garmin_connector)
        existing_files = set(os.path.basename(p) for p in filestore.list_existing_fit_files(configuration.fit_dir_path))

        processed = []

        for activity in garmin_activities:
            try:
                activity_id = activity["activityId"]
                activity_type = activity["activityType"]["typeKey"]
                start_time = datetime.strptime(activity["startTimeGMT"], "%Y-%m-%d %H:%M:%S")
                # print(f"Start time z biblioteki: {start_time}")
                activity_date = start_time.date()
                # activity_start_temp = activity["startTimeLocal"]
                # print(f"TYP: {type(activity_start_temp)}")
                activity_db_id = datetime_to_id(start_time)

                if activity_db_id in db_ids:
                    logger.info("Activity %s already exists in DB.", activity_db_id)
                    continue

                fit_filename = filestore.build_fit_filename(activity_date, activity_type, activity_id)
                fit_filepath = os.path.join(configuration.fit_dir_path, fit_filename)

                if fit_filename in existing_files:
                    # File already downloaded; parse and save to DB
                    logger.info("File %s already downloaded, but not saved in DB", fit_filename)
                    parsed_activity = filestore.parse_fit_file(fit_filepath)
                    actitity_to_save = activity_mapper.prepare_activity_data_to_save_in_db(parsed_activity)
                    activity_repository.save_activity_to_db(database, actitity_to_save)
                    processed.append(fit_filepath)
                    continue

                # Download from Garmin as ZIP, then extract to .fit
                fit_data = garmin_connector.download_activity(
                    activity_id, dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL)

                zip_filename = filestore.build_zip_filename(activity_date, activity_type, activity_id)
                fit_path_zip = os.path.join(configuration.fit_dir_path, zip_filename)

                try:
                    with open(fit_path_zip, "wb") as f:
                        f.write(fit_data)
                except Exception:
                    logger.exception("Failed to save ZIP file %s", fit_path_zip)
                    continue

                try:
                    with zipfile.ZipFile(fit_path_zip, "r") as zip_ref:
                        for member in zip_ref.namelist():
                            new_filepath = fit_filepath
                            with zip_ref.open(member) as source, open(new_filepath, "wb") as target:
                                target.write(source.read())
                    try:
                        os.remove(fit_path_zip)
                    except FileNotFoundError:
                        pass
                except Exception:
                    logger.exception("Failed to extract or remove ZIP %s", fit_path_zip)
                    continue

                # Parse and save to DB
                parsed_activity = filestore.parse_fit_file(fit_filepath)
                actitity_to_save = activity_mapper.prepare_activity_data_to_save_in_db(parsed_activity)
                activity_repository.save_activity_to_db(database, actitity_to_save)

                processed.append(fit_filepath)
            except Exception:
                logger.exception("Failed processing activity")

        logger.info("Synced activities (files processed): %d", len(processed))
        return processed
