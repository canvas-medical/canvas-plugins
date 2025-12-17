import pytest

from canvas_sdk.clients.twillio.structures.helper import Helper


@pytest.mark.parametrize(
    ("raw_body", "expected"),
    [
        pytest.param(
            "",
            {},
            id="empty_string",
        ),
        pytest.param(
            ("parm0=theParm0&parm1=theParm1&parm2=theParm2&parm3=theParm3"),
            {
                "parm0": "theParm0",
                "parm1": "theParm1",
                "parm2": "theParm2",
                "parm3": "theParm3",
            },
            id="single_values",
        ),
        pytest.param(
            (
                "parm0=theParm0"
                "&parm1=theParm1"
                "&parm1=theParmX"
                "&parm2=theParm2"
                "&parm2=theParmY"
                "&parm3=theParm3"
            ),
            {
                "parm0": "theParm0",
                "parm1": ["theParm1", "theParmX"],
                "parm2": ["theParm2", "theParmY"],
                "parm3": "theParm3",
            },
            id="multiple_values",
        ),
    ],
)
def test_parse_body(raw_body: str, expected: dict) -> None:
    """Test Helper.parse_body correctly parses URL-encoded strings with single and multiple values."""
    test = Helper
    result = test.parse_body(raw_body)
    assert result == expected
