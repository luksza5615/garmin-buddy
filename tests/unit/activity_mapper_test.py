import pytest

from app.ingestion.activity_mapper import ActivityMapper

@pytest.fixture(scope="module")
def activity_mapper() -> ActivityMapper:
    return ActivityMapper()

@pytest.fixture(scope="module")
def activity_id() -> int:
    return 1

def test_empty_values_set_to_default(activity_mapper, activity_id, activity_dict_empty_values):

    activity = activity_mapper.from_parsed_fit(activity_id, activity_dict_empty_values)

    for key in [
        "activity_start_time",
        "sport", 
        "subsport",
        "elapsed_duration", 
        "distance_in_km",   
        "avg_heart_rate",
        "grade_adjusted_avg_pace_min_per_km",
        "calories_burnt",
        "aerobic_training_effect_0_to_5",
        "anaerobic_training_effect_0_to_5",
        "total_ascent_in_m",
        "total_descent_in_m"]:
        assert  getattr(activity, key) is None