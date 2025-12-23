import logging
import os
from pathlib import Path


logger = logging.getLogger(__name__)

class FitFileStore:
    def __init__(self):
        pass

    def list_existing_fit_files(self, fit_dir_path: Path):
        files = []
        try:
            for f in os.listdir(fit_dir_path):
                full = os.path.join(fit_dir_path, f)
                if os.path.isfile(full) and f.lower().endswith(".fit"):
                    files.append(full)
        except FileNotFoundError:
            pass
        return files
    
    def build_fit_filename(self, activity_date, activity_type, activity_id):
        return f"{activity_date}_{activity_type}_{activity_id}.fit"


    def build_zip_filename(self, activity_date, activity_type, activity_id):
        return f"{activity_date}_{activity_type}_{activity_id}.zip"

 


if __name__ == '__main__':
    fitservice = FitFileStore()
    path = "C:\\Users\\LSzata\\OneDrive - DXC Production\\Projects\\garmin\\garmin-buddy\\tests\\app_test\\services\\resources\\2025-03-25_running_18635294298.fit"
    from app.services.db_service import ActivityRepository
    from app.services.activity_mapper import ActivityMapper
    from app.database.db_connector import Database
    from app.config import Config
    from app.services.fit_parser import FitParser
    parser = FitParser()
    parsed = parser.parse_fit_file(path)
    activity_mapper = ActivityMapper()
    activity_to_save = activity_mapper.from_parsed_fit(parsed)
    repository = ActivityRepository()
    configuration = Config.from_env()
    from app.services.sync_service import SyncService
    sync_service = SyncService()
    database = Database.create_db(configuration)
    sync_service.sync_activities(configuration, database)
