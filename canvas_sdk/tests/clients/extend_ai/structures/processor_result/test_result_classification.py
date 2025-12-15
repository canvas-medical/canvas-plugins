from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.structures.processor_result.insight import Insight
from canvas_sdk.clients.extend_ai.structures.processor_result.result_classification import (
    ResultClassification,
)
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that Classification is a dataclass with the expected field types."""
    tested = ResultClassification
    fields = {
        "type": str,
        "confidence": float,
        "insights": list[Insight],
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "type": "medical_record",
                "confidence": 0.95,
                "insights": [
                    {"type": "diagnosis", "content": "Type 2 Diabetes"},
                    {"type": "medication", "content": "Metformin 500mg"},
                ],
            },
            ResultClassification(
                type="medical_record",
                confidence=0.95,
                insights=[
                    Insight(type="diagnosis", content="Type 2 Diabetes"),
                    Insight(type="medication", content="Metformin 500mg"),
                ],
            ),
            id="classification_multiple_insights",
        ),
        pytest.param(
            {
                "type": "prescription",
                "confidence": 0.99,
                "insights": [],
            },
            ResultClassification(
                type="prescription",
                confidence=0.99,
                insights=[],
            ),
            id="classification_no_insights",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test Classification.from_dict correctly deserializes classification results from API responses."""
    tested = ResultClassification
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            ResultClassification(
                type="medical_record",
                confidence=0.95,
                insights=[
                    Insight(type="diagnosis", content="Type 2 Diabetes"),
                    Insight(type="medication", content="Metformin 500mg"),
                ],
            ),
            {
                "type": "medical_record",
                "confidence": 0.95,
                "insights": [
                    {"type": "diagnosis", "content": "Type 2 Diabetes"},
                    {"type": "medication", "content": "Metformin 500mg"},
                ],
            },
            id="classification_multiple_insights",
        ),
        pytest.param(
            ResultClassification(
                type="lab_report",
                confidence=0.87456,
                insights=[
                    Insight(type="test", content="Complete Blood Count"),
                ],
            ),
            {
                "type": "lab_report",
                "confidence": 0.87,
                "insights": [
                    {"type": "test", "content": "Complete Blood Count"},
                ],
            },
            id="with_rounding",
        ),
        pytest.param(
            ResultClassification(
                type="prescription",
                confidence=0.99,
                insights=[],
            ),
            {
                "type": "prescription",
                "confidence": 0.99,
                "insights": [],
            },
            id="classification_no_insights",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test Classification.to_dict correctly serializes classification results for API requests."""
    result = tested.to_dict()
    assert result == expected
