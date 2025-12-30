import logging
import os
import zipfile

from app.config import Config
from app.services.garmin_client import GarminClient

logger = logging.getLogger(__name__)

class FitFileStore:
    def __init__(self, configuration: Config):
        self.fit_dir_path = configuration.fit_dir_path

    def list_existing_fit_files_ids_set(self):
        files_ids = set()  
        for file in os.listdir(self.fit_dir_path):
            file_id = self.extract_id_from_fit_file(file)
            files_ids.add(file_id)
        return files_ids

    def build_fit_filename(self, activity_date, activity_type, activity_id):
        return f"{activity_date}_{activity_type}_{activity_id}.fit"

    def build_zip_filename(self, activity_date, activity_type, activity_id):
        return f"{activity_date}_{activity_type}_{activity_id}.zip"

    def extract_id_from_fit_file(self, fit_file_name):
        id_extension = fit_file_name.split('_')[-1]
        return id_extension[:-4]
    
    def create_fit_file_from_zip(self, fit_zip_file, garmin_activity, fit_filepath, garmin_client: GarminClient) -> None:
        garmin_activity_id, garmin_activity_type, garmin_activity_date = garmin_client.get_activity_signature(garmin_activity)
        zip_filename = self.build_zip_filename(garmin_activity_date, garmin_activity_type, garmin_activity_id)
        fit_path_zip = os.path.join(self.fit_dir_path, zip_filename)

        try:
            with open(fit_path_zip, "wb") as f:
                f.write(fit_zip_file)
        except Exception:
            logger.exception("Failed to save ZIP file %s", fit_path_zip)

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


if __name__ == '__main__':
    
    #path = "C:\\Users\\LSzata\\OneDrive - DXC Production\\Projects\\garmin\\fit-files\\2024-01-26_hiit_13677470616.fit"
    path = "C:\\Users\\LSzata\\OneDrive - DXC Production\\Projects\\garmin\\fit-files\\2025-12-28_running_21372303473.fit"
    fit_dir_path = "C:\\Users\\LSzata\\OneDrive - DXC Production\\Projects\\garmin\\fit-files"
    from app.services.db_service import ActivityRepository
    from app.services.activity_mapper import ActivityMapper
    from app.database.db_connector import Database
    from app.config import Config
    from app.services.fit_parser import FitParser
    configuration = Config.from_env()
    parser = FitParser()
    parsed = parser.parse_fit_file(path)
    # print(parsed)
    fitservice = FitFileStore(configuration)
    activity_mapper = ActivityMapper()
    activity_to_save = activity_mapper.from_parsed_fit(123456, parsed)
    print(activity_to_save)
    # repository = ActivityRepository()
    # from app.services.sync_service import SyncService
    # sync_service = SyncService()
    # database = Database.create_db(configuration)
    # sync_service.sync_activities(configuration, database)
    # id = fitservice.extract_id_from_fit_file("2023-11-24_multi_sport_12859996495.fit")
    # files_ids = fitservice.list_existing_fit_files_ids(fit_dir_path)
    # print(files_ids)
