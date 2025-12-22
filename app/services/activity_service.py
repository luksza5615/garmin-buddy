import logging
from app.utils.converter import datetime_to_id, convert_m_to_km, calculate_start_of_week, convert_seconds_to_time, convert_speed_to_pace

logger = logging.getLogger(__name__)

class ActivityMapper:
    def __init__(self) -> None:
        pass
        
    def modify_subsport(self, sport, subsport):
        if sport == "hiking":
            subsport = "hiking"
        if sport == "running" and subsport == "generic":
            subsport = "outdoor_running"

        return subsport


    def calculate_efficiency_index(self, pace, avg_hr):
        # Expect "m:ss"; if missing/invalid, return None
        if not pace or ":" not in pace or avg_hr in (None, 0):
            return None
        minutes, seconds = pace.split(":")
        minutes = int(minutes)
        seconds = int(seconds)
        adjusted_pace = minutes + seconds / 60
        efficiency_index = round((100000 / (adjusted_pace * avg_hr)), 2)
        return efficiency_index


    def prepare_activity_data_to_save_in_db(self, parsed_activity_data):
        activity_id = datetime_to_id(parsed_activity_data.get("start_time"))

        subsport = self.modify_subsport(parsed_activity_data.get(
            "sport"), parsed_activity_data.get("sub_sport"))

        grade_adjusted_avg_pace_min_per_km = convert_speed_to_pace(
            parsed_activity_data.get("enhanced_avg_speed"))

        if parsed_activity_data.get("sport") == "running":
            running_efficiency_index = self.calculate_efficiency_index(
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

        logger.debug("Activity data being saved in DB:\n %s", activity_data_to_save_in_db)

        return activity_data_to_save_in_db