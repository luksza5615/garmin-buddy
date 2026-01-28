import pytest

from app.utils.converter import convert_m_to_km


@pytest.mark.parametrize(
    "meters, expected",
    [
        (None, None),
        (0.00, 0.00),
        (0, 0.00),
        (14000, 14.00),
        (14009.95, 14.01),
    ],
)
def test_convert_m_to_km(meters: float | None, expected: str) -> None:
    assert convert_m_to_km(meters) == expected
