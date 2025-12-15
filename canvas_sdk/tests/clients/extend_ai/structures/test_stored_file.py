from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.structures.stored_file import StoredFile
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that StoredFile is a dataclass with the expected field types."""
    tested = StoredFile
    fields = {
        "id": str,
        "type": str,
        "name": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "id": "file123",
                "type": "application/pdf",
                "name": "document.pdf",
            },
            StoredFile(
                id="file123",
                type="application/pdf",
                name="document.pdf",
            ),
            id="pdf_file",
        ),
        pytest.param(
            {
                "id": "file456",
                "type": "image/png",
                "name": "image.png",
            },
            StoredFile(
                id="file456",
                type="image/png",
                name="image.png",
            ),
            id="png_file",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test StoredFile.from_dict correctly deserializes file metadata from API responses."""
    tested = StoredFile
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            StoredFile(
                id="file123",
                type="application/pdf",
                name="document.pdf",
            ),
            {
                "id": "file123",
                "type": "application/pdf",
                "name": "document.pdf",
            },
            id="pdf_file",
        ),
        pytest.param(
            StoredFile(
                id="file456",
                type="image/png",
                name="image.png",
            ),
            {
                "id": "file456",
                "type": "image/png",
                "name": "image.png",
            },
            id="png_file",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test StoredFile.to_dict correctly serializes file metadata for API requests."""
    result = tested.to_dict()
    assert result == expected
