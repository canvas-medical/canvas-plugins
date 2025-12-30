import pytest

from canvas_sdk.clients.twilio.structures.capabilities import Capabilities
from canvas_sdk.clients.twilio.structures.request_failed import RequestFailed
from canvas_sdk.clients.twilio.structures.sms_mms import SmsMms
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test SmsMms dataclass has correct field types."""
    tested = SmsMms
    fields = {
        "number_from": str,
        "number_from_sid": str,
        "number_to": str,
        "message": str,
        "media_url": str,
        "status_callback_url": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("sms_mms", "expected"),
    [
        pytest.param(
            SmsMms(
                number_from="+11234567890",
                number_from_sid="PN123",
                number_to="+11234567891",
                message="Hello World",
                media_url="",
                status_callback_url="https://example.com/status",
            ),
            {
                "number_from": "+11234567890",
                "number_from_sid": "PN123",
                "number_to": "+11234567891",
                "message": "Hello World",
                "media_url": "",
                "status_callback_url": "https://example.com/status",
            },
            id="sms_with_callback",
        ),
        pytest.param(
            SmsMms(
                number_from="+11234567892",
                number_from_sid="PN456",
                number_to="+11234567893",
                message="",
                media_url="https://example.com/image.jpg",
                status_callback_url="",
            ),
            {
                "number_from": "+11234567892",
                "number_from_sid": "PN456",
                "number_to": "+11234567893",
                "message": "",
                "media_url": "https://example.com/image.jpg",
                "status_callback_url": "",
            },
            id="mms_only",
        ),
    ],
)
def test_to_dict(sms_mms: SmsMms, expected: dict) -> None:
    """Test SmsMms.to_dict converts instance to dictionary."""
    result = sms_mms.to_dict()
    assert result == expected


@pytest.mark.parametrize(
    ("sms_mms", "capabilities", "expected"),
    [
        pytest.param(
            SmsMms(
                number_from="+11234567890",
                number_from_sid="PN123",
                number_to="+11234567891",
                message="Hello World",
                media_url="",
                status_callback_url="",
            ),
            Capabilities(fax=False, mms=False, sms=True, voice=False),
            {
                "To": "+11234567891",
                "From": "+11234567890",
                "Body": "Hello World",
            },
            id="sms_only_with_sms_capability",
        ),
        pytest.param(
            SmsMms(
                number_from="+11234567892",
                number_from_sid="PN456",
                number_to="+11234567893",
                message="",
                media_url="https://example.com/image.jpg",
                status_callback_url="",
            ),
            Capabilities(fax=False, mms=True, sms=False, voice=False),
            {
                "To": "+11234567893",
                "From": "+11234567892",
                "MediaUrl": "https://example.com/image.jpg",
            },
            id="mms_only_with_mms_capability",
        ),
        pytest.param(
            SmsMms(
                number_from="+11234567894",
                number_from_sid="PN789",
                number_to="+11234567895",
                message="Hello with image",
                media_url="https://example.com/photo.png",
                status_callback_url="https://example.com/status",
            ),
            Capabilities(fax=False, mms=True, sms=True, voice=False),
            {
                "To": "+11234567895",
                "From": "+11234567894",
                "Body": "Hello with image",
                "MediaUrl": "https://example.com/photo.png",
                "StatusCallback": "https://example.com/status",
            },
            id="sms_and_mms_with_callback",
        ),
        pytest.param(
            SmsMms(
                number_from="+11234567896",
                number_from_sid="PN999",
                number_to="+11234567897",
                message="Text only",
                media_url="",
                status_callback_url="https://example.com/callback",
            ),
            Capabilities(fax=False, mms=True, sms=True, voice=True),
            {
                "To": "+11234567897",
                "From": "+11234567896",
                "Body": "Text only",
                "StatusCallback": "https://example.com/callback",
            },
            id="sms_with_callback_full_capabilities",
        ),
    ],
)
def test_to_api(sms_mms: SmsMms, capabilities: Capabilities, expected: dict) -> None:
    """Test SmsMms.to_api converts instance to API format with capability validation."""
    result = sms_mms.to_api(capabilities)
    assert result == expected


@pytest.mark.parametrize(
    ("sms_mms", "capabilities", "expected_error"),
    [
        pytest.param(
            SmsMms(
                number_from="+11234567890",
                number_from_sid="PN123",
                number_to="+11234567891",
                message="Hello",
                media_url="",
                status_callback_url="",
            ),
            Capabilities(fax=False, mms=False, sms=False, voice=False),
            "+11234567890 cannot sent SMS",
            id="no_sms_capability",
        ),
        pytest.param(
            SmsMms(
                number_from="+11234567892",
                number_from_sid="PN456",
                number_to="+11234567893",
                message="",
                media_url="https://example.com/image.jpg",
                status_callback_url="",
            ),
            Capabilities(fax=False, mms=False, sms=True, voice=False),
            "+11234567892 cannot sent MMS",
            id="no_mms_capability",
        ),
        pytest.param(
            SmsMms(
                number_from="+11234567894",
                number_from_sid="PN789",
                number_to="+11234567895",
                message="",
                media_url="",
                status_callback_url="",
            ),
            Capabilities(fax=False, mms=True, sms=True, voice=False),
            "no content to be sent",
            id="no_content",
        ),
    ],
)
def test_to_api__raises_request_failed(
    sms_mms: SmsMms, capabilities: Capabilities, expected_error: str
) -> None:
    """Test SmsMms.to_api raises RequestFailed when capabilities are insufficient or no content."""
    with pytest.raises(RequestFailed) as exc_info:
        sms_mms.to_api(capabilities)
    assert exc_info.value.status_code == 0
    assert exc_info.value.message == expected_error
