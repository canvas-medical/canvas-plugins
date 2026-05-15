from datetime import datetime
from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.structures.processor_meta import ProcessorMeta
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that ProcessorMeta is a dataclass with the expected field types."""
    tested = ProcessorMeta
    fields = {
        "id": str,
        "name": str,
        "type": ProcessorType,
        "created_at": datetime | None,
        "updated_at": datetime | None,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "id": "proc123",
                "name": "My Processor",
                "type": "EXTRACT",
                "createdAt": "2024-01-15T10:30:00",
                "updatedAt": "2024-01-16T14:20:00",
            },
            ProcessorMeta(
                id="proc123",
                name="My Processor",
                type=ProcessorType.EXTRACT,
                created_at=datetime(2024, 1, 15, 10, 30, 0),
                updated_at=datetime(2024, 1, 16, 14, 20, 0),
            ),
            id="extract_processor",
        ),
        pytest.param(
            {
                "id": "proc456",
                "name": "Another Processor",
                "type": "CLASSIFY",
                "createdAt": "2024-02-20T08:15:30",
                "updatedAt": "2024-02-21T09:45:15",
            },
            ProcessorMeta(
                id="proc456",
                name="Another Processor",
                type=ProcessorType.CLASSIFY,
                created_at=datetime(2024, 2, 20, 8, 15, 30),
                updated_at=datetime(2024, 2, 21, 9, 45, 15),
            ),
            id="classify_processor",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test ProcessorMeta.from_dict correctly deserializes processor metadata from API responses."""
    tested = ProcessorMeta
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            ProcessorMeta(
                id="proc123",
                name="My Processor",
                type=ProcessorType.EXTRACT,
                created_at=datetime(2024, 1, 15, 10, 30, 0),
                updated_at=datetime(2024, 1, 16, 14, 20, 0),
            ),
            {
                "id": "proc123",
                "name": "My Processor",
                "type": "EXTRACT",
                "createdAt": "2024-01-15T10:30:00",
                "updatedAt": "2024-01-16T14:20:00",
            },
            id="extract_processor",
        ),
        pytest.param(
            ProcessorMeta(
                id="proc456",
                name="Another Processor",
                type=ProcessorType.CLASSIFY,
                created_at=datetime(2024, 2, 20, 8, 15, 30),
                updated_at=datetime(2024, 2, 21, 9, 45, 15),
            ),
            {
                "id": "proc456",
                "name": "Another Processor",
                "type": "CLASSIFY",
                "createdAt": "2024-02-20T08:15:30",
                "updatedAt": "2024-02-21T09:45:15",
            },
            id="classify_processor",
        ),
        pytest.param(
            ProcessorMeta(
                id="proc789",
                name="Null Dates Processor",
                type=ProcessorType.SPLITTER,
                created_at=None,
                updated_at=None,
            ),
            {
                "id": "proc789",
                "name": "Null Dates Processor",
                "type": "SPLITTER",
                "createdAt": None,
                "updatedAt": None,
            },
            id="splitter_processor_null_dates",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test ProcessorMeta.to_dict correctly serializes processor metadata for API requests."""
    result = tested.to_dict()
    assert result == expected
