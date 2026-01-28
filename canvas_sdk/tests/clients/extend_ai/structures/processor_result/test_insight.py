from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.structures.processor_result.insight import Insight
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that Insight is a dataclass with the expected field types."""
    tested = Insight
    fields = {
        "type": str,
        "content": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "type": "diagnosis",
                "content": "Type 2 Diabetes Mellitus",
            },
            Insight(
                type="diagnosis",
                content="Type 2 Diabetes Mellitus",
            ),
            id="full_content",
        ),
        pytest.param(
            {
                "type": "observation",
                "content": "",
            },
            Insight(
                type="observation",
                content="",
            ),
            id="empty_content",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test Insight.from_dict correctly deserializes insight data from API responses."""
    tested = Insight
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            Insight(
                type="diagnosis",
                content="Type 2 Diabetes Mellitus",
            ),
            {
                "type": "diagnosis",
                "content": "Type 2 Diabetes Mellitus",
            },
            id="full_content",
        ),
        pytest.param(
            Insight(
                type="observation",
                content="",
            ),
            {
                "type": "observation",
                "content": "",
            },
            id="empty_content",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test Insight.to_dict correctly serializes insight data for API requests."""
    result = tested.to_dict()
    assert result == expected
