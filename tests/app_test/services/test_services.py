import pytest
import os
from app.services.fit_parser import parse_fit_file


@pytest.fixture
def get_file():
    return os.path.join(os.path.dirname(__file__), "resources", "2025-03-25_running_18635294298.fit")


def test_parse_fit_file(get_file):
    result = parse_fit_file(get_file)
    print(result)
    assert result is not None
    assert isinstance(result, dict)
