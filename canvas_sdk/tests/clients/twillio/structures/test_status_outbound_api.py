import pytest

from canvas_sdk.clients.twillio.constants.message_status import MessageStatus
from canvas_sdk.clients.twillio.structures.status_outbound_api import StatusOutboundApi
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test StatusOutboundApi dataclass has correct field types."""
    tested = StatusOutboundApi
    fields = {
        "account_sid": str,
        "message_sid": str,
        "sms_sid": str,
        "sms_status": MessageStatus,
        "message_status": MessageStatus,
        "number_to": str,
        "number_from": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "AccountSid": "theAccountSid",
                "MessageSid": "theMessageSid",
                "SmsSid": "theSmsSid",
                "SmsStatus": "sent",
                "MessageStatus": "sent",
                "To": "+11234567890",
                "From": "+11234567891",
            },
            StatusOutboundApi(
                account_sid="theAccountSid",
                message_sid="theMessageSid",
                sms_sid="theSmsSid",
                sms_status=MessageStatus.SENT,
                message_status=MessageStatus.SENT,
                number_to="+11234567890",
                number_from="+11234567891",
            ),
            id="sent_status",
        ),
        pytest.param(
            {
                "AccountSid": "theAccountSid2",
                "MessageSid": "theMessageSid2",
                "SmsSid": "theSmsSid2",
                "SmsStatus": "delivered",
                "MessageStatus": "delivered",
                "To": "+11234567892",
                "From": "+11234567893",
            },
            StatusOutboundApi(
                account_sid="theAccountSid2",
                message_sid="theMessageSid2",
                sms_sid="theSmsSid2",
                sms_status=MessageStatus.DELIVERED,
                message_status=MessageStatus.DELIVERED,
                number_to="+11234567892",
                number_from="+11234567893",
            ),
            id="delivered_status",
        ),
        pytest.param(
            {
                "AccountSid": "theAccountSid3",
                "MessageSid": "theMessageSid3",
                "SmsSid": "theSmsSid3",
                "SmsStatus": "failed",
                "MessageStatus": "failed",
                "To": "+11234567894",
                "From": "+11234567895",
            },
            StatusOutboundApi(
                account_sid="theAccountSid3",
                message_sid="theMessageSid3",
                sms_sid="theSmsSid3",
                sms_status=MessageStatus.FAILED,
                message_status=MessageStatus.FAILED,
                number_to="+11234567894",
                number_from="+11234567895",
            ),
            id="failed_status",
        ),
    ],
)
def test_from_dict(data: dict, expected: StatusOutboundApi) -> None:
    """Test StatusOutboundApi.from_dict creates instance from dictionary with various statuses."""
    test = StatusOutboundApi
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("raw_body", "expected"),
    [
        pytest.param(
            (
                "AccountSid=theAccountSid"
                "&MessageSid=theMessageSid"
                "&SmsSid=theSmsSid"
                "&SmsStatus=sent"
                "&MessageStatus=sent"
                "&To=%2B11234567890"
                "&From=%2B11234567891"
            ),
            StatusOutboundApi(
                account_sid="theAccountSid",
                message_sid="theMessageSid",
                sms_sid="theSmsSid",
                sms_status=MessageStatus.SENT,
                message_status=MessageStatus.SENT,
                number_to="+11234567890",
                number_from="+11234567891",
            ),
            id="sent_status",
        ),
        pytest.param(
            (
                "AccountSid=theAccountSid2"
                "&MessageSid=theMessageSid2"
                "&SmsSid=theSmsSid2"
                "&SmsStatus=delivered"
                "&MessageStatus=delivered"
                "&To=%2B11234567892"
                "&From=%2B11234567893"
            ),
            StatusOutboundApi(
                account_sid="theAccountSid2",
                message_sid="theMessageSid2",
                sms_sid="theSmsSid2",
                sms_status=MessageStatus.DELIVERED,
                message_status=MessageStatus.DELIVERED,
                number_to="+11234567892",
                number_from="+11234567893",
            ),
            id="delivered_status",
        ),
    ],
)
def test_callback_outbound_api(raw_body: str, expected: StatusOutboundApi) -> None:
    """Test StatusOutboundApi.callback_outbound_api parses raw URL-encoded body and creates instance."""
    test = StatusOutboundApi
    result = test.callback_outbound_api(raw_body)
    assert result == expected
