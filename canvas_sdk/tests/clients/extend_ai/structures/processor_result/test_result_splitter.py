from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.structures.processor_result.result_splitter import (
    ResultSplitter,
)
from canvas_sdk.clients.extend_ai.structures.processor_result.split import Split
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that Splitter is a dataclass with the expected field types."""
    tested = ResultSplitter
    fields = {
        "splits": list[Split],
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "splits": [
                    {
                        "type": "lab_result",
                        "observation": "Blood test results",
                        "identifier": "LAB-001",
                        "startPage": 1,
                        "endPage": 3,
                        "classificationId": "class-123",
                        "id": "split-456",
                        "fileId": "file-789",
                        "name": "CBC Results",
                    },
                    {
                        "type": "prescription",
                        "observation": "Medication order",
                        "identifier": "RX-002",
                        "startPage": 5,
                        "endPage": 5,
                        "classificationId": "class-456",
                        "id": "split-789",
                        "fileId": "file-012",
                        "name": "Metformin Prescription",
                    },
                ]
            },
            ResultSplitter(
                splits=[
                    Split(
                        type="lab_result",
                        observation="Blood test results",
                        identifier="LAB-001",
                        startPage=1,
                        endPage=3,
                        classificationId="class-123",
                        id="split-456",
                        fileId="file-789",
                        name="CBC Results",
                    ),
                    Split(
                        type="prescription",
                        observation="Medication order",
                        identifier="RX-002",
                        startPage=5,
                        endPage=5,
                        classificationId="class-456",
                        id="split-789",
                        fileId="file-012",
                        name="Metformin Prescription",
                    ),
                ]
            ),
            id="multiple_splits",
        ),
        pytest.param(
            {
                "splits": [
                    {
                        "type": "imaging",
                        "observation": "X-ray report",
                        "identifier": "IMG-003",
                        "startPage": 10,
                        "endPage": 15,
                        "classificationId": "class-789",
                        "id": "split-012",
                        "fileId": "file-345",
                        "name": "Chest X-ray",
                    }
                ]
            },
            ResultSplitter(
                splits=[
                    Split(
                        type="imaging",
                        observation="X-ray report",
                        identifier="IMG-003",
                        startPage=10,
                        endPage=15,
                        classificationId="class-789",
                        id="split-012",
                        fileId="file-345",
                        name="Chest X-ray",
                    )
                ]
            ),
            id="single_split",
        ),
        pytest.param(
            {"splits": []},
            ResultSplitter(splits=[]),
            id="empty_splits",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test Splitter.from_dict correctly deserializes splitter results from API responses."""
    tested = ResultSplitter
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            ResultSplitter(
                splits=[
                    Split(
                        type="lab_result",
                        observation="Blood test results",
                        identifier="LAB-001",
                        startPage=1,
                        endPage=3,
                        classificationId="class-123",
                        id="split-456",
                        fileId="file-789",
                        name="CBC Results",
                    ),
                    Split(
                        type="prescription",
                        observation="Medication order",
                        identifier="RX-002",
                        startPage=5,
                        endPage=5,
                        classificationId="class-456",
                        id="split-789",
                        fileId="file-012",
                        name="Metformin Prescription",
                    ),
                ]
            ),
            {
                "splits": [
                    {
                        "type": "lab_result",
                        "observation": "Blood test results",
                        "identifier": "LAB-001",
                        "startPage": 1,
                        "endPage": 3,
                        "classificationId": "class-123",
                        "id": "split-456",
                        "fileId": "file-789",
                        "name": "CBC Results",
                    },
                    {
                        "type": "prescription",
                        "observation": "Medication order",
                        "identifier": "RX-002",
                        "startPage": 5,
                        "endPage": 5,
                        "classificationId": "class-456",
                        "id": "split-789",
                        "fileId": "file-012",
                        "name": "Metformin Prescription",
                    },
                ]
            },
            id="multiple_splits",
        ),
        pytest.param(
            ResultSplitter(
                splits=[
                    Split(
                        type="imaging",
                        observation="X-ray report",
                        identifier="IMG-003",
                        startPage=10,
                        endPage=15,
                        classificationId="class-789",
                        id="split-012",
                        fileId="file-345",
                        name="Chest X-ray",
                    )
                ]
            ),
            {
                "splits": [
                    {
                        "type": "imaging",
                        "observation": "X-ray report",
                        "identifier": "IMG-003",
                        "startPage": 10,
                        "endPage": 15,
                        "classificationId": "class-789",
                        "id": "split-012",
                        "fileId": "file-345",
                        "name": "Chest X-ray",
                    }
                ]
            },
            id="single_split",
        ),
        pytest.param(
            ResultSplitter(splits=[]),
            {"splits": []},
            id="empty_splits",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test Splitter.to_dict correctly serializes splitter results for API requests."""
    result = tested.to_dict()
    assert result == expected
