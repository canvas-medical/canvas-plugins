import pytest

from canvas_sdk.clients.sendgrid.structures.parsed_attachment import ParsedAttachment
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test ParsedAttachment dataclass has correct field types."""
    tested = ParsedAttachment
    fields = {
        "filename": str,
        "name": str,
        "type": str,
        "content_id": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "filename": "document.pdf",
                "name": "document",
                "type": "application/pdf",
                "content-id": "attach123",
            },
            ParsedAttachment(
                filename="document.pdf",
                name="document",
                type="application/pdf",
                content_id="attach123",
            ),
            id="pdf_attachment",
        ),
        pytest.param(
            {
                "filename": "image.png",
                "name": "logo",
                "type": "image/png",
                "content-id": "img456",
            },
            ParsedAttachment(
                filename="image.png",
                name="logo",
                type="image/png",
                content_id="img456",
            ),
            id="image_attachment",
        ),
    ],
)
def test_from_dict(data: dict, expected: ParsedAttachment) -> None:
    """Test ParsedAttachment.from_dict creates instance from dictionary."""
    test = ParsedAttachment
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("attachment", "expected"),
    [
        pytest.param(
            ParsedAttachment(
                filename="document.pdf",
                name="document",
                type="application/pdf",
                content_id="attach123",
            ),
            {
                "filename": "document.pdf",
                "name": "document",
                "type": "application/pdf",
                "contentId": "attach123",
            },
            id="pdf_attachment",
        ),
        pytest.param(
            ParsedAttachment(
                filename="spreadsheet.xlsx",
                name="data",
                type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                content_id="sheet789",
            ),
            {
                "filename": "spreadsheet.xlsx",
                "name": "data",
                "type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "contentId": "sheet789",
            },
            id="spreadsheet_attachment",
        ),
    ],
)
def test_to_dict(attachment: ParsedAttachment, expected: dict) -> None:
    """Test ParsedAttachment.to_dict converts instance to dictionary."""
    result = attachment.to_dict()
    assert result == expected
