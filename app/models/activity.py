from dataclasses import dataclass
from datetime import date, time, timedelta
from app.utils.converter import datetime_to_id, convert_m_to_km, calculate_start_of_week, convert_seconds_to_time, convert_speed_to_pace

@dataclass
class Activity:
    activity_id: int
    activity_date: date
    activity_start_time: time
    sport: str
    subsport: str
    distance_in_km: float
    elapsed_duration: timedelta
    grade_adjusted_avg_pace_min_per_km: float
    avg_heart_rate: int
    calories_burnt: int
    aerobic_training_effect_0_to_5: float
    anaerobic_training_effect_0_to_5: float
    total_ascent_in_meters: int
    total_descent_in_meters: int
    start_of_week: date
    running_efficiency_index: float