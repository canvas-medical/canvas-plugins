from canvas_sdk.clients.sendgrid.structures.parsed_attachment import ParsedAttachment
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Verify ParsedAttachment is a frozen dataclass with correct fields."""
    tested = ParsedAttachment
    fields = {
        "filename": str,
        "name": str,
        "type": str,
        "content_id": str,
    }
    result = is_dataclass(tested, fields)
    expected = True
    assert result is expected


def test_from_dict() -> None:
    """Test creating ParsedAttachment from dictionary."""
    tested = ParsedAttachment
    data = {
        "filename": "document.pdf",
        "name": "document",
        "type": "application/pdf",
        "content-id": "abc123",
    }
    result = tested.from_dict(data)
    expected = ParsedAttachment(
        filename="document.pdf",
        name="document",
        type="application/pdf",
        content_id="abc123",
    )
    assert result == expected


def test_to_dict() -> None:
    """Test converting ParsedAttachment to dictionary."""
    tested = ParsedAttachment(
        filename="image.png",
        name="image",
        type="image/png",
        content_id="xyz789",
    )
    result = tested.to_dict()
    expected = {
        "filename": "image.png",
        "name": "image",
        "type": "image/png",
        "contentId": "xyz789",
    }
    assert result == expected
