import logging
import os
import zipfile

from app.config import Config
from app.ingestion.garmin_client import GarminClient

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



