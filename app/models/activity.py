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
    total_ascent_in_meters: int
    total_descent_in_meters: int
    start_of_week: date
    running_efficiency_index: float

    @classmethod
    def create_activity(cls) -> "Activity":
        activity_id = 123456789
        activity_date = date(2025, 12, 18)
        activity_start_time = time(18, 42, 0)
        sport = "running"
        subsport = "trail"
        distance_in_km = 14.7
        elapsed_duration = time(1, 0, 0)
        grade_adjusted_avg_pace_min_per_km = 4.55
        avg_heart_rate = 154
        calories_burnt = 1080
        aerobic_training_effect_0_to_5 = 4.2
        anaerobic_training_effect_0_to_5 = 2.1
        total_ascent_in_meters = 620
        total_descent_in_meters = 615
        start_of_week = date(2025, 12, 16)
        running_efficiency_index = 52.8

        return cls(
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
