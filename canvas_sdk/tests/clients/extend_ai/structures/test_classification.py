from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.structures.classification import Classification
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that Classification is a dataclass with the expected field types."""
    tested = Classification
    fields = {
        "id": str,
        "type": str,
        "description": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "id": "class1",
                "type": "invoice",
                "description": "Invoice documents",
            },
            Classification(
                id="class1",
                type="invoice",
                description="Invoice documents",
            ),
            id="basic_classification",
        ),
        pytest.param(
            {
                "id": "class2",
                "type": "medical_record",
                "description": "Patient medical records",
            },
            Classification(
                id="class2",
                type="medical_record",
                description="Patient medical records",
            ),
            id="medical_classification",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test Classification.from_dict correctly deserializes classification data from API responses."""
    tested = Classification
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            Classification(
                id="class1",
                type="invoice",
                description="Invoice documents",
            ),
            {
                "id": "class1",
                "type": "invoice",
                "description": "Invoice documents",
            },
            id="basic_classification",
        ),
        pytest.param(
            Classification(
                id="class2",
                type="medical_record",
                description="Patient medical records",
            ),
            {
                "id": "class2",
                "type": "medical_record",
                "description": "Patient medical records",
            },
            id="medical_classification",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test Classification.to_dict correctly serializes classification data for API requests."""
    result = tested.to_dict()
    assert result == expected
