
import logging
from datetime import datetime, timedelta
from garminconnect import Garmin

logger = logging.getLogger(__name__)

class GarminClient:
    def __init__(self, email, password):
        self.email = email
        self.password = password
    
    def login_to_garmin(self):
        try:
            garmin_connection = Garmin(self.email, self.password)
            garmin_connection.login()
            logger.info("Connected to garmin")
            return garmin_connection
        except Exception:
            logger.exception("Failed to connect.")
            raise

    def get_garmin_activities_full_history(self, garmin_connection, start_date=None, end_date=None, window_days=90):
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
                activities = garmin_connection.get_activities_by_date(
                    window_start.isoformat(), window_end.isoformat())
                if activities:
                    all_activities.extend(activities)
            except Exception as e:
                logger.exception("Failed to fetch activities for window %s - %s", window_start, window_end)
            window_start = window_end + timedelta(days=1)

        return all_activities
    
