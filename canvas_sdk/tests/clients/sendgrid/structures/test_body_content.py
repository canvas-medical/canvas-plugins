import pytest

from canvas_sdk.clients.sendgrid.structures.body_content import BodyContent
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test BodyContent dataclass has correct field types."""
    tested = BodyContent
    fields = {
        "type": str,
        "value": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("body_content", "expected"),
    [
        pytest.param(
            BodyContent(type="text/plain", value="Hello World"),
            {"type": "text/plain", "value": "Hello World"},
            id="plain_text",
        ),
        pytest.param(
            BodyContent(type="text/html", value="<h1>Hello World</h1>"),
            {"type": "text/html", "value": "<h1>Hello World</h1>"},
            id="html_content",
        ),
    ],
)
def test_to_dict(body_content: BodyContent, expected: dict) -> None:
    """Test BodyContent.to_dict converts instance to dictionary."""
    result = body_content.to_dict()
    assert result == expected
