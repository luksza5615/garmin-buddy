from datetime import date, timedelta
from typing import Any, Tuple

import pandas as pd

from app.database.db_service import ActivityRepository

_DEFAULT_END_DATE = date.today()
_DEFAULT_START_DATE = date.today() - timedelta(7)
_MAX_ALLOWED_RANGE = 1000

class AnalysisService:
    def __init__(self, repository: ActivityRepository) -> None:
        self.repository = repository

    def calculate_kpis(self, activities: pd.DataFrame) -> dict[str, float]:
        if activities.empty:
            return {}

        kpis = {}
        kpis["activities_count"] = float(len(activities))

        if "distance_in_km" in activities.columns:
            kpis["distance_km"] = float(activities["distance_in_km"].sum())
        # TODO
        # if "elapsed_duration" in activities.columns:
        #     kpis["duration_h"] = float(activities["elapsed_duration"].dt.total_seconds().sum() / 3600)
        if "total_ascent_in_m" in activities.columns:
            kpis["ascent_m"] = float(activities["total_ascent_in_m"].sum())
        if "avg_heart_rate" in activities.columns:
            kpis["avg_hr"] = float(activities["avg_heart_rate"].mean())
        if "calories_burnt" in activities.columns:
            kpis["calories_burnt"] = float(activities["calories_burnt"].sum())
        if "aerobic_training_effect_0_to_5" in activities.columns:
            kpis["aerobic_training_effect_0_to_5"] = float(activities["aerobic_training_effect_0_to_5"].mean())
        if "anerobic_training_effect_0_to_5" in activities.columns:
            kpis["anaerobic_training_effect_0_to_5"] = float(activities["anaerobic_training_effect_0_to_5"].mean())

        return kpis

    # TODO to be checked if used
    def calculate_basic_metrics(self, start_date: date = _DEFAULT_START_DATE, end_date: date = _DEFAULT_END_DATE) -> dict[str, Any]:
        is_exceeded, delta = self._max_range_exceeded(start_date, end_date)

        if is_exceeded is True:
            raise ValueError(
                f"Maximum allowed activities range exceeded. Selected: {delta} days. Allowed: {_MAX_ALLOWED_RANGE}"
            )
        
        activities_df = self.repository.get_activities(start_date, end_date)

        running_df = activities_df.loc[activities_df["sport"] == "running"]

        metrics = {
            "number_of_activities": len(running_df),
            "avg_running_hr": running_df["avg_heart_rate"].mean(),
            "total_distance_in_km": running_df["distance_in_km"].sum(),
            "total_ascent_in_m": running_df["total_ascent_in_m"].sum(),
            "calories_burnt": running_df["calories_burnt"].sum(),
            "avg_running_efficiency_index": running_df["running_efficiency_index"].mean(),
            "aerobic_training_effect_0_to_5": running_df["aerobic_training_effect_0_to_5"].mean(),
            "anaerobic_training_effect_0_to_5": running_df["anaerobic_training_effect_0_to_5"].mean(),
        }

        return metrics

    def weekly_running_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        
        running_df = df[df["sport"] == "running"].copy()

        weekly_stats = (
            running_df.groupby("start_of_week", as_index=False)
            .agg(
                distance_km=("distance_in_km", "sum"),
                avg_hr=("avg_heart_rate", "mean"),
                ascent_m=("total_ascent_in_m", "sum"),
                calories=("calories_burnt", "sum"),
                te_aer=("aerobic_training_effect_0_to_5", "mean"),
                te_ana=("anaerobic_training_effect_0_to_5", "mean"),
                rei=("running_efficiency_index", "mean"),
            )
            .sort_values("start_of_week", ascending=False)
        )

        return weekly_stats

    #TODO
    # def _calculate_total_activity_time(self, df: pd.DataFrame) 
    #TODO check if used
    def _max_range_exceeded(self, start_date: date, end_date: date) -> Tuple[bool, int]:
        delta = (end_date - start_date).days
        is_exceeded = True if delta >= _MAX_ALLOWED_RANGE else False
        
        return is_exceeded, delta
        
    #TODO
    print("test")

    