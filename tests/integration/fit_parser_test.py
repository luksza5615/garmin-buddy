from pathlib import Path
import pytest

from app.ingestion.fit_parser import FitParser

@pytest.fixture(scope="module")
def fit_parser() -> FitParser:
    return FitParser()

def test_parse_fit_file_is_not_empty_dict(fit_file, fit_parser):
    result = fit_parser.parse_fit_file(fit_file)
    assert isinstance(result, dict) and result

@pytest.mark.parametrize(
    "fname, expected_sport, expected_distance",
    [
        ("2025-03-25_running_18635294298.fit", "running", 9175.13),
        ("2026-01-16_strength_training_21569092921.fit", "training", 0.0)
    ],
)
def test_parsed_fit_file_basic_fields(fit_parser, fit_files_parent, fname, expected_sport, expected_distance):
    file_path = Path(fit_files_parent) / fname
    activity = fit_parser.parse_fit_file(file_path)

    for key in ["sport", "total_elapsed_time", "total_calories", "avg_heart_rate", "total_distance"]:
        assert key in activity
    
    assert activity["total_calories"] > 0
    assert activity["total_elapsed_time"] > 0
    assert activity["avg_heart_rate"] > 0
    assert activity["sport"] == expected_sport
    assert activity["total_distance"] == expected_distance



    

