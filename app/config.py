import os
import logging
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Config:
    fit_dir_path: Path
    garmin_email: str
    garmin_password: str

    @classmethod
    def from_env(cls) -> "Config":
        
        load_dotenv(override=True)

        fit_path = os.getenv("FIT_DIR_PATH")
        garmin_email = os.getenv("GARMIN_EMAIL")
        garmin_password = os.getenv("GARMIN_PASSWORD")
        db_connection_string = os.getenv("DB_CONNECTION_STRING")
        
        missing_vars = []
        if not fit_path:
            missing_vars.append("FIT_DIR_PATH")  
        if not garmin_email:
            missing_vars.append("GARMIN_EMAIL")
        if not garmin_password:
            missing_vars.append("GARMIN_PASSWORD")
        
        if missing_vars:
            logging.exception("Mising vars: %s", missing_vars)
            raise RuntimeError(
                f"Missing required variables {', '.join(missing_vars)}"
            )

        return cls(
            fit_dir_path=fit_path,
            garmin_email=garmin_email,
            garmin_password=garmin_password,
            db_connection_string=db_connection_string
        )