import pytest

from canvas_sdk.clients.sendgrid.structures.parsed_header import ParsedHeader
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test ParsedHeader dataclass has correct field types."""
    tested = ParsedHeader
    fields = {
        "name": str,
        "value": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        pytest.param(
            ParsedHeader(name="Content-Type", value="text/html; charset=UTF-8"),
            {"name": "Content-Type", "value": "text/html; charset=UTF-8"},
            id="content_type_header",
        ),
        pytest.param(
            ParsedHeader(name="From", value="sender@example.com"),
            {"name": "From", "value": "sender@example.com"},
            id="from_header",
        ),
        pytest.param(
            ParsedHeader(name="Subject", value="Important: Meeting Tomorrow"),
            {"name": "Subject", "value": "Important: Meeting Tomorrow"},
            id="subject_header",
        ),
    ],
)
def test_to_dict(header: ParsedHeader, expected: dict) -> None:
    """Test ParsedHeader.to_dict converts instance to dictionary."""
    result = header.to_dict()
    assert result == expected
