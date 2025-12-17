import logging
from garminconnect import Garmin

logger = logging.getLogger(__name__)


def login_to_garmin(email, password):
    try:
        garmin_connector = Garmin(email, password)
        garmin_connector.login()
        logger.info("Connected to garmin")
        return garmin_connector
    except Exception:
        logger.exception("Failed to connect.")
        raise
