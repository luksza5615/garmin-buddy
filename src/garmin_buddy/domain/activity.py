from dataclasses import dataclass
from datetime import date, time, timedelta


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
    total_ascent_in_m: int
    total_descent_in_m: int
    start_of_week: date
    running_efficiency_index: float
