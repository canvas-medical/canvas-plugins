from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.structures.config.part_range import PartRange
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that PartRange is a dataclass with the expected field types."""
    tested = PartRange
    fields = {
        "start": int,
        "end": int,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {"start": 1, "end": 10},
            PartRange(start=1, end=10),
            id="range_1_to_10",
        ),
        pytest.param(
            {"start": 5, "end": 15},
            PartRange(start=5, end=15),
            id="range_5_to_15",
        ),
        pytest.param(
            {"start": "10", "end": "20"},
            PartRange(start=10, end=20),
            id="string_conversion_10_to_20",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test PartRange.from_dict correctly deserializes page range data with string-to-int conversion."""
    tested = PartRange
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            PartRange(start=1, end=10),
            {"start": 1, "end": 10},
            id="range_1_to_10",
        ),
        pytest.param(
            PartRange(start=5, end=15),
            {"start": 5, "end": 15},
            id="range_5_to_15",
        ),
        pytest.param(
            PartRange(start=10, end=20),
            {"start": 10, "end": 20},
            id="range_10_to_20",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test PartRange.to_dict correctly serializes page range data for API requests."""
    result = tested.to_dict()
    assert result == expected
