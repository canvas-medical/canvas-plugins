import pytest

from canvas_sdk.clients.twilio.structures.helper import Helper


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
        pytest.param(
            "key1=&key2=value2&key3=",
            {
                "key1": "",
                "key2": "value2",
                "key3": "",
            },
            id="blank_values",
        ),
        pytest.param(
            "name=John+Doe&message=Hello+World",
            {
                "name": "John Doe",
                "message": "Hello World",
            },
            id="plus_signs_as_spaces",
        ),
        pytest.param(
            "encoded=%2B1234567890&special=%40%23%24%25",
            {
                "encoded": "+1234567890",
                "special": "@#$%",
            },
            id="url_encoded_special_chars",
        ),
        pytest.param(
            "unicode=%E2%9C%93&emoji=%F0%9F%92%AF",
            {
                "unicode": "✓",
                "emoji": "💯",
            },
            id="url_encoded_unicode",
        ),
        pytest.param(
            "mixed=value1&mixed=&mixed=value2",
            {
                "mixed": ["value1", "", "value2"],
            },
            id="multiple_values_with_blank",
        ),
        pytest.param(
            "key=value&key=value&key=value",
            {
                "key": ["value", "value", "value"],
            },
            id="same_value_multiple_times",
        ),
        pytest.param(
            "From=%2B15551234567&To=%2B15559876543&Body=Test+message",
            {
                "From": "+15551234567",
                "To": "+15559876543",
                "Body": "Test message",
            },
            id="twilio_callback_format",
        ),
    ],
)
def test_parse_body(raw_body: str, expected: dict) -> None:
    """Test Helper.parse_body correctly parses URL-encoded strings with single and multiple values."""
    test = Helper
    result = test.parse_body(raw_body)
    assert result == expected
