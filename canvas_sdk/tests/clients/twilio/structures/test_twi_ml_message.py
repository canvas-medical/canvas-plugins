from unittest.mock import patch

import pytest

from canvas_sdk.clients.twilio.constants.constants import _Constants
from canvas_sdk.clients.twilio.constants.http_method import HttpMethod
from canvas_sdk.clients.twilio.structures.twi_ml_message import TwiMlMessage
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test TwiMlMessage dataclass has correct field types."""
    tested = TwiMlMessage
    fields = {
        "number_to": str,
        "number_from": str,
        "status_callback_url": str,
        "message_text": str,
        "media_url": str,
        "method": HttpMethod | None,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("message_text", "expected"),
    [
        pytest.param(
            "Hello World",
            TwiMlMessage(
                number_to="",
                number_from="",
                status_callback_url="",
                message_text="Hello World",
                media_url="",
                method=None,
            ),
            id="simple_message",
        ),
        pytest.param(
            "Long message text",
            TwiMlMessage(
                number_to="",
                number_from="",
                status_callback_url="",
                message_text="Long message text",
                media_url="",
                method=None,
            ),
            id="longer_message",
        ),
    ],
)
def test_instance(message_text: str, expected: TwiMlMessage) -> None:
    """Test TwiMlMessage.instance creates instance with only message text."""
    test = TwiMlMessage
    result = test.instance(message_text)
    assert result == expected


@pytest.mark.parametrize(
    ("message_text", "media_url", "expected"),
    [
        pytest.param(
            "Hello with image",
            "https://example.com/image.jpg",
            TwiMlMessage(
                number_to="",
                number_from="",
                status_callback_url="",
                message_text="Hello with image",
                media_url="https://example.com/image.jpg",
                method=None,
            ),
            id="message_with_image",
        ),
        pytest.param(
            "Video message",
            "https://example.com/video.mp4",
            TwiMlMessage(
                number_to="",
                number_from="",
                status_callback_url="",
                message_text="Video message",
                media_url="https://example.com/video.mp4",
                method=None,
            ),
            id="message_with_video",
        ),
    ],
)
def test_instance_with_media(message_text: str, media_url: str, expected: TwiMlMessage) -> None:
    """Test TwiMlMessage.instance_with_media creates instance with message text and media."""
    test = TwiMlMessage
    result = test.instance_with_media(message_text, media_url)
    assert result == expected


@pytest.mark.parametrize(
    ("twi_ml_message", "expected"),
    [
        pytest.param(
            TwiMlMessage(
                number_to="",
                number_from="",
                status_callback_url="",
                message_text="Hello World",
                media_url="",
                method=None,
            ),
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response><Message>Hello World</Message></Response>",
            id="simple_message_without_attributes",
        ),
        pytest.param(
            TwiMlMessage(
                number_to="+11234567891",
                number_from="+11234567890",
                status_callback_url="https://example.com/status",
                message_text="Hello with attributes",
                media_url="",
                method=HttpMethod.POST,
            ),
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>"
            '<Message to="+11234567891" from="+11234567890" statusCallback="https://example.com/status" method="POST">'
            "Hello with attributes</Message></Response>",
            id="message_with_all_attributes",
        ),
        pytest.param(
            TwiMlMessage(
                number_to="+11234567891",
                number_from="+11234567890",
                status_callback_url="",
                message_text="Hello with partial attributes",
                media_url="",
                method=None,
            ),
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>"
            '<Message to="+11234567891" from="+11234567890">'
            "Hello with partial attributes"
            "</Message>"
            "</Response>",
            id="message_with_partial_attributes",
        ),
        pytest.param(
            TwiMlMessage(
                number_to="",
                number_from="",
                status_callback_url="",
                message_text="Hello with media",
                media_url="https://example.com/image.jpg",
                method=None,
            ),
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>"
            "<Message>"
            "<Body>Hello with media</Body>"
            "<Media>https://example.com/image.jpg</Media>"
            "</Message>"
            "</Response>",
            id="message_with_media_separate_body",
        ),
    ],
)
def test_to_xml(twi_ml_message: TwiMlMessage, expected: str) -> None:
    """Test TwiMlMessage.to_xml generates valid TwiML XML with correct structure."""
    result = twi_ml_message.to_xml()
    assert result == expected


@pytest.mark.parametrize(
    ("message_text", "max_length", "exp_in_xml"),
    [
        pytest.param(
            "abcdefghi",
            9,
            "abcdefghi",
            id="exactly_max_length",
        ),
        pytest.param(
            "abcdefghijklmno",
            9,
            "abcdefghi",
            id="over_max_length",
        ),
    ],
)
def test_to_xml__truncates_long_message(
    message_text: str, max_length: int, exp_in_xml: str
) -> None:
    """Test TwiMlMessage.to_xml truncates message text to max SMS length."""
    twi_ml_message = TwiMlMessage(
        number_to="",
        number_from="",
        status_callback_url="",
        message_text=message_text,
        media_url="",
        method=None,
    )

    # Create a new Constants instance with the test max_length
    mock_constants = _Constants(
        sms_max_length=max_length,
        standard_date="%Y-%m-%dT%H:%M:%S%z",
        twilio_date="%a, %d %b %Y %H:%M:%S %z",
    )

    with patch("canvas_sdk.clients.twilio.structures.twi_ml_message.Constants", mock_constants):
        result = twi_ml_message.to_xml()

    # The truncated text should be in the XML
    assert exp_in_xml in result
    # The full text should not be present if it was truncated
    if message_text != exp_in_xml:
        assert message_text not in result


@pytest.mark.parametrize(
    ("twi_ml_message", "expected"),
    [
        pytest.param(
            TwiMlMessage(
                number_to="",
                number_from="",
                status_callback_url="",
                message_text="Test",
                media_url="",
                method=None,
            ),
            {},
            id="no_attributes",
        ),
        pytest.param(
            TwiMlMessage(
                number_to="+11234567891",
                number_from="+11234567890",
                status_callback_url="https://example.com/status",
                message_text="Test",
                media_url="",
                method=HttpMethod.POST,
            ),
            {
                "to": "+11234567891",
                "from": "+11234567890",
                "statusCallback": "https://example.com/status",
                "method": "POST",
            },
            id="all_attributes",
        ),
        pytest.param(
            TwiMlMessage(
                number_to="+11234567891",
                number_from="",
                status_callback_url="",
                message_text="Test",
                media_url="",
                method=None,
            ),
            {
                "to": "+11234567891",
            },
            id="only_to_attribute",
        ),
        pytest.param(
            TwiMlMessage(
                number_to="",
                number_from="+11234567890",
                status_callback_url="https://example.com/callback",
                message_text="Test",
                media_url="",
                method=HttpMethod.GET,
            ),
            {
                "from": "+11234567890",
                "statusCallback": "https://example.com/callback",
                "method": "GET",
            },
            id="from_callback_and_method",
        ),
    ],
)
def test__build_attributes(twi_ml_message: TwiMlMessage, expected: dict) -> None:
    """Test TwiMlMessage._build_attributes returns only non-empty attributes."""
    result = twi_ml_message._build_attributes()
    assert result == expected
