from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.structures.processor_result.result_extraction import (
    ResultExtraction,
)
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that Extraction is a dataclass with the expected field types."""
    tested = ResultExtraction
    fields = {
        "value": dict,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "value": {
                    "patient_name": "John Doe",
                    "date_of_birth": "1980-05-15",
                    "diagnosis": "Hypertension",
                }
            },
            ResultExtraction(
                value={
                    "patient_name": "John Doe",
                    "date_of_birth": "1980-05-15",
                    "diagnosis": "Hypertension",
                }
            ),
            id="patient_data_extraction",
        ),
        pytest.param(
            {"value": {}},
            ResultExtraction(value={}),
            id="empty_extraction",
        ),
        pytest.param(
            {
                "value": {
                    "nested": {
                        "field": "value",
                        "another": {"deep": "data"},
                    }
                }
            },
            ResultExtraction(
                value={
                    "nested": {
                        "field": "value",
                        "another": {"deep": "data"},
                    }
                }
            ),
            id="nested_data_extraction",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test Extraction.from_dict correctly deserializes extraction results from API responses."""
    tested = ResultExtraction
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            ResultExtraction(
                value={
                    "patient_name": "John Doe",
                    "date_of_birth": "1980-05-15",
                    "diagnosis": "Hypertension",
                }
            ),
            {
                "value": {
                    "patient_name": "John Doe",
                    "date_of_birth": "1980-05-15",
                    "diagnosis": "Hypertension",
                }
            },
            id="patient_data_extraction",
        ),
        pytest.param(
            ResultExtraction(value={}),
            {"value": {}},
            id="empty_extraction",
        ),
        pytest.param(
            ResultExtraction(
                value={
                    "nested": {
                        "field": "value",
                        "another": {"deep": "data"},
                    }
                }
            ),
            {
                "value": {
                    "nested": {
                        "field": "value",
                        "another": {"deep": "data"},
                    }
                }
            },
            id="nested_data_extraction",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test Extraction.to_dict correctly serializes extraction results for API requests."""
    result = tested.to_dict()
    assert result == expected
