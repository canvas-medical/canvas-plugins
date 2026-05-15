from canvas_sdk.clients.sendgrid.structures.parsed_header import ParsedHeader
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Verify ParsedHeader is a frozen dataclass with correct fields."""
    tested = ParsedHeader
    fields = {
        "name": str,
        "value": str,
    }
    result = is_dataclass(tested, fields)
    expected = True
    assert result is expected


def test_to_dict() -> None:
    """Test converting ParsedHeader to dictionary."""
    tested = ParsedHeader(
        name="Content-Type",
        value="text/plain; charset=utf-8",
    )
    result = tested.to_dict()
    expected = {
        "name": "Content-Type",
        "value": "text/plain; charset=utf-8",
    }
    assert result == expected
