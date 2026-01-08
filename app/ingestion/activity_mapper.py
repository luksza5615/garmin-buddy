import logging
from typing import Any

from app.domain.activity import Activity
from app.utils.converter import (
    calculate_start_of_week,
    convert_m_to_km,
    convert_seconds_to_time,
    convert_speed_to_pace,
)

logger = logging.getLogger(__name__)

class ActivityMapper:
    def from_parsed_fit(self, activity_id: int, parsed_activity: dict[str, Any]) -> Activity:
        activity_id = activity_id
        activity_start_time = parsed_activity.get("local_timestamp") or parsed_activity.get("start_time") or parsed_activity.get("timestamp")
        activity_date = activity_start_time.date()
        sport = parsed_activity.get("sport")
        subsport = self._modify_subsport(sport, parsed_activity.get("sub_sport"))
        distance_in_km = convert_m_to_km(parsed_activity.get("total_distance"))
        elapsed_duration = convert_seconds_to_time(parsed_activity.get("total_elapsed_time"))
        grade_adjusted_avg_pace_min_per_km = convert_speed_to_pace(parsed_activity.get("enhanced_avg_speed"))
        avg_heart_rate = parsed_activity.get("avg_heart_rate")
        calories_burnt = parsed_activity.get("total_calories")
        aerobic_training_effect_0_to_5 = parsed_activity.get("total_training_effect")
        anaerobic_training_effect_0_to_5 = parsed_activity.get("total_anaerobic_training_effect")
        total_ascent_in_meters = parsed_activity.get("total_ascent")
        total_descent_in_meters = parsed_activity.get("total_descent")
        start_of_week = calculate_start_of_week(activity_start_time)
        running_efficiency_index = self._calculate_running_efficiency_index(sport, grade_adjusted_avg_pace_min_per_km, avg_heart_rate)
        
        return Activity(
            activity_id=activity_id,
            activity_date=activity_date,
            activity_start_time=activity_start_time,
            sport=sport,
            subsport=subsport,
            distance_in_km=distance_in_km,
            elapsed_duration=elapsed_duration,
            grade_adjusted_avg_pace_min_per_km=grade_adjusted_avg_pace_min_per_km,
            avg_heart_rate=avg_heart_rate,
            calories_burnt=calories_burnt,
            aerobic_training_effect_0_to_5=aerobic_training_effect_0_to_5,
            anaerobic_training_effect_0_to_5=anaerobic_training_effect_0_to_5,
            total_ascent_in_meters=total_ascent_in_meters,
            total_descent_in_meters=total_descent_in_meters,
            start_of_week=start_of_week,
            running_efficiency_index=running_efficiency_index
        )

    def _modify_subsport(self, sport: str, subsport: str) -> str:
        if sport == "hiking":
            subsport = "hiking"
        if sport == "running" and subsport == "generic":
            subsport = "outdoor_running"

        return subsport

    def _calculate_running_efficiency_index(self, sport: str, pace: str, avg_hr: int) -> float:
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
  