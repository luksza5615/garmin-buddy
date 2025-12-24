import logging
import datetime
from app.utils.converter import datetime_to_id, convert_m_to_km, calculate_start_of_week, convert_seconds_to_time, convert_speed_to_pace
from app.models.activity import Activity

logger = logging.getLogger(__name__)

class ActivityMapper:
    def __init__(self) -> None:
        pass
    
    def from_parsed_fit(self, parsed_activity: dict):
        # activity_id = 12345678999
        activity_id = datetime_to_id(parsed_activity["start_time"])
        activity_date = parsed_activity["local_timestamp"]
        activity_start_time = parsed_activity["local_timestamp"]
        # activity_start_time = datetime.datetime(2025, 3, 25, 18, 4, 40)
        sport = parsed_activity["sport"]
        subsport = self.modify_subsport(parsed_activity["sport"], parsed_activity["sub_sport"])
        distance_in_km = convert_m_to_km(parsed_activity["total_distance"])
        elapsed_duration = convert_seconds_to_time(parsed_activity["total_elapsed_time"])
        grade_adjusted_avg_pace_min_per_km = convert_speed_to_pace(parsed_activity["enhanced_avg_speed"])
        avg_heart_rate = parsed_activity["avg_heart_rate"]
        calories_burnt = parsed_activity["total_calories"]
        aerobic_training_effect_0_to_5 = parsed_activity["total_training_effect"]
        anaerobic_training_effect_0_to_5 = parsed_activity["total_anaerobic_training_effect"]
        total_ascent_in_meters = parsed_activity.get("total_descent", 0)
        total_descent_in_meters = parsed_activity.get("total_descent", 0)
        start_of_week = calculate_start_of_week(parsed_activity["timestamp"])
        running_efficiency_index = self.calculate_efficiency_index(parsed_activity["sport"], convert_speed_to_pace(parsed_activity["enhanced_avg_speed"]), parsed_activity["avg_heart_rate"])
        
        return Activity(
            activity_id,
            activity_date,
            activity_start_time,
            sport,
            subsport,
            distance_in_km,
            elapsed_duration,
            grade_adjusted_avg_pace_min_per_km,
            avg_heart_rate,
            calories_burnt,
            aerobic_training_effect_0_to_5,
            anaerobic_training_effect_0_to_5,
            total_ascent_in_meters,
            total_descent_in_meters,
            start_of_week,
            running_efficiency_index
        )

    def modify_subsport(self, sport, subsport):
        if sport == "hiking":
            subsport = "hiking"
        if sport == "running" and subsport == "generic":
            subsport = "outdoor_running"

        return subsport


    def calculate_efficiency_index(self, sport, pace, avg_hr):
        # Expect "m:ss"; if missing/invalid, return None
        if sport == 'running':
            if not pace or ":" not in pace or avg_hr in (None, 0):
                return None
            minutes, seconds = pace.split(":")
            minutes = int(minutes)
            seconds = int(seconds)
            adjusted_pace = minutes + seconds / 60
            efficiency_index = round((100000 / (adjusted_pace * avg_hr)), 2)
            return efficiency_index
        else:
            return None
  