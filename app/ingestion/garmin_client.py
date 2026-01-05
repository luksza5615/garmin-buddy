
import logging
from datetime import datetime, timedelta
from garminconnect import Garmin

logger = logging.getLogger(__name__)

class GarminClient:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self._client: Garmin
    
    def test_zones(self):
        timezones = self._client.get_activity_hr_in_timezones(21401639665)
        print(timezones)

    def login_to_garmin(self):
        try:
            client = Garmin(self.email, self.password)
            client.login()
            self._client = client            
            logger.info("Connected to garmin")
        except Exception:
            logger.exception("Failed to connect.")
            raise

    def get_garmin_activities_history(self, start_date=None, end_date=None, window_days=90):
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
                activities = self._client.get_activities_by_date(
                    window_start.isoformat(), window_end.isoformat())
                if activities:
                    all_activities.extend(activities)
            except Exception as e:
                logger.exception("Failed to fetch activities for window %s - %s", window_start, window_end)
            window_start = window_end + timedelta(days=1)

        return all_activities
    
    def download_activity_as_zip_file(self, activity_id):
        return self._client.download_activity(
            activity_id, dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL)

    def get_activity_signature(self, garmin_activity) -> tuple:
        garmin_activity_id = garmin_activity["activityId"]
        garmin_activity_type = garmin_activity["activityType"]["typeKey"]
        garmin_activity_start_time = datetime.strptime(garmin_activity["startTimeGMT"], "%Y-%m-%d %H:%M:%S")
        garmin_activity_date = garmin_activity_start_time.date()
        
        return garmin_activity_id, garmin_activity_type, garmin_activity_date
    
