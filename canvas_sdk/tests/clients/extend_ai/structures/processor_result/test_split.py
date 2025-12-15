from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.structures.processor_result.split import Split
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that Split is a dataclass with the expected field types."""
    tested = Split
    fields = {
        "type": str,
        "observation": str,
        "identifier": str,
        "startPage": int,
        "endPage": int,
        "classificationId": str,
        "id": str,
        "fileId": str,
        "name": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
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
            id="lab_result_split",
        ),
        pytest.param(
            {
                "type": "imaging",
                "observation": "X-ray report",
                "identifier": "IMG-003",
                "startPage": 10,
                "endPage": 15,
                "classificationId": "class-789",
                "id": "split-012",
                "fileId": "file-345",
            },
            Split(
                type="imaging",
                observation="X-ray report",
                identifier="IMG-003",
                startPage=10,
                endPage=15,
                classificationId="class-789",
                id="split-012",
                fileId="file-345",
                name="",
            ),
            id="split_without_name",
        ),
        pytest.param(
            {
                "type": "progress_note",
                "observation": "Patient visit",
                "identifier": "NOTE-004",
                "startPage": "20",
                "endPage": "22",
                "classificationId": "class-012",
                "id": "split-345",
                "fileId": "file-678",
                "name": None,
            },
            Split(
                type="progress_note",
                observation="Patient visit",
                identifier="NOTE-004",
                startPage=20,
                endPage=22,
                classificationId="class-012",
                id="split-345",
                fileId="file-678",
                name="",
            ),
            id="split_with_string_pages_and_null_name",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test Split.from_dict correctly deserializes split results from API responses."""
    tested = Split
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
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
            id="lab_result_split",
        ),
        pytest.param(
            Split(
                type="imaging",
                observation="X-ray report",
                identifier="IMG-003",
                startPage=10,
                endPage=15,
                classificationId="class-789",
                id="split-012",
                fileId="file-345",
                name="",
            ),
            {
                "type": "imaging",
                "observation": "X-ray report",
                "identifier": "IMG-003",
                "startPage": 10,
                "endPage": 15,
                "classificationId": "class-789",
                "id": "split-012",
                "fileId": "file-345",
                "name": "",
            },
            id="split_without_name",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test Split.to_dict correctly serializes split results for API requests."""
    result = tested.to_dict()
    assert result == expected
