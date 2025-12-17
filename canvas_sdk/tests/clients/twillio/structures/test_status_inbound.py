import pytest

from canvas_sdk.clients.twillio.constants.message_status import MessageStatus
from canvas_sdk.clients.twillio.structures.status_inbound import StatusInbound
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test StatusInbound dataclass has correct field types."""
    tested = StatusInbound
    fields = {
        "account_sid": str,
        "message_sid": str,
        "messaging_service_sid": str,
        "sms_message_sid": str,
        "sms_sid": str,
        "sms_status": MessageStatus,
        "to_country": str,
        "to_zip": str,
        "to_state": str,
        "to_city": str,
        "from_country": str,
        "from_zip": str,
        "from_state": str,
        "from_city": str,
        "number_to": str,
        "number_from": str,
        "body": str,
        "count_media": int,
        "count_segments": int,
        "media_content_type": list[str],
        "media_url": list[str],
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "ToCountry": "theToCountry",
                "ToState": "theToState",
                "SmsMessageSid": "theSmsMessageSid",
                "NumMedia": "0",
                "ToCity": "theToCity",
                "FromZip": "theFromZip",
                "SmsSid": "theSmsSid",
                "FromState": "theFromState",
                "SmsStatus": "delivered",
                "FromCity": "theFromCity",
                "Body": "theBody",
                "FromCountry": "theFromCountry",
                "To": "+11234567890",
                "MessagingServiceSid": "theMessagingServiceSid",
                "ToZip": "theToZip",
                "NumSegments": "1",
                "MessageSid": "theMessageSid",
                "AccountSid": "theAccountSid",
                "From": "+11234567891",
                "ApiVersion": "2010-04-01",
            },
            StatusInbound(
                account_sid="theAccountSid",
                message_sid="theMessageSid",
                messaging_service_sid="theMessagingServiceSid",
                sms_message_sid="theSmsMessageSid",
                sms_sid="theSmsSid",
                sms_status=MessageStatus.DELIVERED,
                to_country="theToCountry",
                to_zip="theToZip",
                to_state="theToState",
                to_city="theToCity",
                from_country="theFromCountry",
                from_zip="theFromZip",
                from_state="theFromState",
                from_city="theFromCity",
                number_to="+11234567890",
                number_from="+11234567891",
                body="theBody",
                count_media=0,
                count_segments=1,
                media_content_type=[],
                media_url=[],
            ),
            id="no_media",
        ),
        pytest.param(
            {
                "ToCountry": "theToCountry",
                "ToState": "theToState",
                "SmsMessageSid": "theSmsMessageSid",
                "NumMedia": "3",
                "MediaContentType0": "theMediaContentType0",
                "MediaUrl0": "theMediaUrl0",
                "MediaContentType1": "theMediaContentType1",
                "MediaUrl1": "theMediaUrl1",
                "MediaContentType2": "theMediaContentType2",
                "MediaUrl2": "theMediaUrl2",
                "ToCity": "theToCity",
                "FromZip": "theFromZip",
                "SmsSid": "theSmsSid",
                "FromState": "theFromState",
                "SmsStatus": "delivered",
                "FromCity": "theFromCity",
                "Body": "theBody",
                "FromCountry": "theFromCountry",
                "To": "+11234567890",
                "MessagingServiceSid": "theMessagingServiceSid",
                "ToZip": "theToZip",
                "NumSegments": "1",
                "MessageSid": "theMessageSid",
                "AccountSid": "theAccountSid",
                "From": "+11234567891",
                "ApiVersion": "2010-04-01",
            },
            StatusInbound(
                account_sid="theAccountSid",
                message_sid="theMessageSid",
                messaging_service_sid="theMessagingServiceSid",
                sms_message_sid="theSmsMessageSid",
                sms_sid="theSmsSid",
                sms_status=MessageStatus.DELIVERED,
                to_country="theToCountry",
                to_zip="theToZip",
                to_state="theToState",
                to_city="theToCity",
                from_country="theFromCountry",
                from_zip="theFromZip",
                from_state="theFromState",
                from_city="theFromCity",
                number_to="+11234567890",
                number_from="+11234567891",
                body="theBody",
                count_media=3,
                count_segments=1,
                media_content_type=[
                    "theMediaContentType0",
                    "theMediaContentType1",
                    "theMediaContentType2",
                ],
                media_url=["theMediaUrl0", "theMediaUrl1", "theMediaUrl2"],
            ),
            id="with_media",
        ),
        pytest.param(
            {
                "ToCountry": "theToCountry",
                "ToState": "theToState",
                "SmsMessageSid": "theSmsMessageSid",
                "NumMedia": "3",
                "MediaContentType0": "theMediaContentType0",
                "MediaUrl0": "theMediaUrl0",
                "MediaContentType1": "theMediaContentType1",
                # missing "MediaUrl1": "theMediaUrl1",
                "MediaContentType2": "theMediaContentType2",
                "MediaUrl2": "theMediaUrl2",
                "ToCity": "theToCity",
                "FromZip": "theFromZip",
                "SmsSid": "theSmsSid",
                "FromState": "theFromState",
                "SmsStatus": "delivered",
                "FromCity": "theFromCity",
                "Body": "theBody",
                "FromCountry": "theFromCountry",
                "To": "+11234567890",
                "MessagingServiceSid": "theMessagingServiceSid",
                "ToZip": "theToZip",
                "NumSegments": "1",
                "MessageSid": "theMessageSid",
                "AccountSid": "theAccountSid",
                "From": "+11234567891",
                "ApiVersion": "2010-04-01",
            },
            StatusInbound(
                account_sid="theAccountSid",
                message_sid="theMessageSid",
                messaging_service_sid="theMessagingServiceSid",
                sms_message_sid="theSmsMessageSid",
                sms_sid="theSmsSid",
                sms_status=MessageStatus.DELIVERED,
                to_country="theToCountry",
                to_zip="theToZip",
                to_state="theToState",
                to_city="theToCity",
                from_country="theFromCountry",
                from_zip="theFromZip",
                from_state="theFromState",
                from_city="theFromCity",
                number_to="+11234567890",
                number_from="+11234567891",
                body="theBody",
                count_media=3,
                count_segments=1,
                media_content_type=["theMediaContentType0"],
                media_url=["theMediaUrl0"],
            ),
            id="with_media_but_missing",
        ),
    ],
)
def test_from_dict(data: dict, expected: StatusInbound) -> None:
    """Test StatusInbound.from_dict creates instance from dictionary with various media configurations."""
    test = StatusInbound
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("raw_body", "expected"),
    [
        pytest.param(
            (
                "ToCountry=theToCountry"
                "&ToState=theToState"
                "&SmsMessageSid=theSmsMessageSid"
                "&NumMedia=0"
                "&ToCity=theToCity"
                "&FromZip=theFromZip"
                "&SmsSid=theSmsSid"
                "&FromState=theFromState"
                "&SmsStatus=delivered"
                "&FromCity=theFromCity"
                "&Body=theBody"
                "&FromCountry=theFromCountry"
                "&To=%2B11234567890"
                "&MessagingServiceSid=theMessagingServiceSid"
                "&ToZip=theToZip"
                "&NumSegments=1"
                "&MessageSid=theMessageSid"
                "&AccountSid=theAccountSid"
                "&From=%2B11234567891"
                "&ApiVersion=2010-04-01"
            ),
            StatusInbound(
                account_sid="theAccountSid",
                message_sid="theMessageSid",
                messaging_service_sid="theMessagingServiceSid",
                sms_message_sid="theSmsMessageSid",
                sms_sid="theSmsSid",
                sms_status=MessageStatus.DELIVERED,
                to_country="theToCountry",
                to_zip="theToZip",
                to_state="theToState",
                to_city="theToCity",
                from_country="theFromCountry",
                from_zip="theFromZip",
                from_state="theFromState",
                from_city="theFromCity",
                number_to="+11234567890",
                number_from="+11234567891",
                body="theBody",
                count_media=0,
                count_segments=1,
                media_content_type=[],
                media_url=[],
            ),
            id="no_media",
        ),
        pytest.param(
            (
                "ToCountry=theToCountry"
                "&ToState=theToState"
                "&SmsMessageSid=theSmsMessageSid"
                "&NumMedia=2"
                "&MediaContentType0=image%2Fjpeg"
                "&MediaUrl0=https%3A%2F%2Fexample.com%2Fimage.jpg"
                "&MediaContentType1=video%2Fmp4"
                "&MediaUrl1=https%3A%2F%2Fexample.com%2Fvideo.mp4"
                "&ToCity=theToCity"
                "&FromZip=theFromZip"
                "&SmsSid=theSmsSid"
                "&FromState=theFromState"
                "&SmsStatus=received"
                "&FromCity=theFromCity"
                "&Body=Message+with+media"
                "&FromCountry=theFromCountry"
                "&To=%2B11234567892"
                "&MessagingServiceSid=theMessagingServiceSid2"
                "&ToZip=theToZip"
                "&NumSegments=1"
                "&MessageSid=theMessageSid2"
                "&AccountSid=theAccountSid2"
                "&From=%2B11234567893"
                "&ApiVersion=2010-04-01"
            ),
            StatusInbound(
                account_sid="theAccountSid2",
                message_sid="theMessageSid2",
                messaging_service_sid="theMessagingServiceSid2",
                sms_message_sid="theSmsMessageSid",
                sms_sid="theSmsSid",
                sms_status=MessageStatus.RECEIVED,
                to_country="theToCountry",
                to_zip="theToZip",
                to_state="theToState",
                to_city="theToCity",
                from_country="theFromCountry",
                from_zip="theFromZip",
                from_state="theFromState",
                from_city="theFromCity",
                number_to="+11234567892",
                number_from="+11234567893",
                body="Message with media",
                count_media=2,
                count_segments=1,
                media_content_type=["image/jpeg", "video/mp4"],
                media_url=["https://example.com/image.jpg", "https://example.com/video.mp4"],
            ),
            id="with_media",
        ),
    ],
)
def test_callback_inbound(raw_body: str, expected: StatusInbound) -> None:
    """Test StatusInbound.callback_inbound parses raw URL-encoded body and creates instance."""
    test = StatusInbound
    result = test.callback_inbound(raw_body)
    assert result == expected
