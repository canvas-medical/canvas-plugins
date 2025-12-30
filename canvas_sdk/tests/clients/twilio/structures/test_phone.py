from datetime import UTC, datetime

import pytest

from canvas_sdk.clients.twilio.constants.http_method import HttpMethod
from canvas_sdk.clients.twilio.structures.capabilities import Capabilities
from canvas_sdk.clients.twilio.structures.phone import Phone
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test Phone dataclass has correct field types."""
    tested = Phone
    fields = {
        "account_sid": str,
        "capabilities": Capabilities,
        "date_created": datetime,
        "date_updated": datetime,
        "friendly_name": str,
        "phone_number": str,
        "sid": str,
        "sms_fallback_method": HttpMethod,
        "sms_fallback_url": str,
        "sms_method": HttpMethod,
        "sms_url": str,
        "status_callback_method": HttpMethod,
        "status_callback": str,
        "status": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "account_sid": "AC123",
                "capabilities": {"fax": False, "mms": True, "sms": True, "voice": True},
                "date_created": "Mon, 15 Dec 2025 10:30:00 +0000",
                "date_updated": "Mon, 15 Dec 2025 10:30:00 +0000",
                "friendly_name": "My SMS Number",
                "phone_number": "+11234567890",
                "sid": "PN456",
                "sms_fallback_method": "POST",
                "sms_fallback_url": "https://example.com/sms-fallback",
                "sms_method": "POST",
                "sms_url": "https://example.com/sms",
                "status_callback_method": "POST",
                "status_callback": "https://example.com/status",
                "status": "in-use",
            },
            Phone(
                account_sid="AC123",
                capabilities=Capabilities(fax=False, mms=True, sms=True, voice=True),
                date_created=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
                date_updated=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
                friendly_name="My SMS Number",
                phone_number="+11234567890",
                sid="PN456",
                sms_fallback_method=HttpMethod.POST,
                sms_fallback_url="https://example.com/sms-fallback",
                sms_method=HttpMethod.POST,
                sms_url="https://example.com/sms",
                status_callback_method=HttpMethod.POST,
                status_callback="https://example.com/status",
                status="in-use",
            ),
            id="full_capabilities",
        ),
        pytest.param(
            {
                "account_sid": "AC789",
                "capabilities": {"fax": False, "mms": False, "sms": True, "voice": False},
                "date_created": "Tue, 16 Dec 2025 14:20:00 +0000",
                "date_updated": "Tue, 16 Dec 2025 14:20:00 +0000",
                "friendly_name": "SMS Only Number",
                "phone_number": "+11234567891",
                "sid": "PN999",
                "sms_fallback_method": "GET",
                "sms_fallback_url": "",
                "sms_method": "GET",
                "sms_url": "https://example.com/sms2",
                "status_callback_method": "GET",
                "status_callback": "",
                "status": "in-use",
            },
            Phone(
                account_sid="AC789",
                capabilities=Capabilities(fax=False, mms=False, sms=True, voice=False),
                date_created=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
                date_updated=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
                friendly_name="SMS Only Number",
                phone_number="+11234567891",
                sid="PN999",
                sms_fallback_method=HttpMethod.GET,
                sms_fallback_url="",
                sms_method=HttpMethod.GET,
                sms_url="https://example.com/sms2",
                status_callback_method=HttpMethod.GET,
                status_callback="",
                status="in-use",
            ),
            id="sms_only",
        ),
    ],
)
def test_from_dict(data: dict, expected: Phone) -> None:
    """Test Phone.from_dict creates instance from dictionary with datetime and capabilities parsing."""
    test = Phone
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("phone", "expected"),
    [
        pytest.param(
            Phone(
                account_sid="AC123",
                capabilities=Capabilities(fax=False, mms=True, sms=True, voice=True),
                date_created=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
                date_updated=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
                friendly_name="My SMS Number",
                phone_number="+11234567890",
                sid="PN456",
                sms_fallback_method=HttpMethod.POST,
                sms_fallback_url="https://example.com/sms-fallback",
                sms_method=HttpMethod.POST,
                sms_url="https://example.com/sms",
                status_callback_method=HttpMethod.POST,
                status_callback="https://example.com/status",
                status="in-use",
            ),
            {
                "account_sid": "AC123",
                "capabilities": {"fax": False, "mms": True, "sms": True, "voice": True},
                "date_created": "Mon, 15 Dec 2025 10:30:00 +0000",
                "date_updated": "Mon, 15 Dec 2025 10:30:00 +0000",
                "created": "2025-12-15T10:30:00+0000",
                "updated": "2025-12-15T10:30:00+0000",
                "friendly_name": "My SMS Number",
                "phone_number": "+11234567890",
                "sid": "PN456",
                "sms_fallback_method": HttpMethod.POST,
                "sms_fallback_url": "https://example.com/sms-fallback",
                "sms_method": HttpMethod.POST,
                "sms_url": "https://example.com/sms",
                "status_callback_method": HttpMethod.POST,
                "status_callback": "https://example.com/status",
                "status": "in-use",
            },
            id="full_capabilities",
        ),
        pytest.param(
            Phone(
                account_sid="AC789",
                capabilities=Capabilities(fax=False, mms=False, sms=True, voice=False),
                date_created=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
                date_updated=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
                friendly_name="SMS Only Number",
                phone_number="+11234567891",
                sid="PN999",
                sms_fallback_method=HttpMethod.GET,
                sms_fallback_url="",
                sms_method=HttpMethod.GET,
                sms_url="https://example.com/sms2",
                status_callback_method=HttpMethod.GET,
                status_callback="",
                status="in-use",
            ),
            {
                "account_sid": "AC789",
                "capabilities": {"fax": False, "mms": False, "sms": True, "voice": False},
                "date_created": "Tue, 16 Dec 2025 14:20:00 +0000",
                "date_updated": "Tue, 16 Dec 2025 14:20:00 +0000",
                "created": "2025-12-16T14:20:00+0000",
                "updated": "2025-12-16T14:20:00+0000",
                "friendly_name": "SMS Only Number",
                "phone_number": "+11234567891",
                "sid": "PN999",
                "sms_fallback_method": HttpMethod.GET,
                "sms_fallback_url": "",
                "sms_method": HttpMethod.GET,
                "sms_url": "https://example.com/sms2",
                "status_callback_method": HttpMethod.GET,
                "status_callback": "",
                "status": "in-use",
            },
            id="sms_only",
        ),
    ],
)
def test_to_dict(phone: Phone, expected: dict) -> None:
    """Test Phone.to_dict converts instance to dictionary with formatted dates."""
    result = phone.to_dict()
    assert result == expected
