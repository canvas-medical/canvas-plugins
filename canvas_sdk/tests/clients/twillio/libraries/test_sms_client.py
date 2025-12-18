from base64 import b64encode
from dataclasses import dataclass
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Self
from unittest.mock import MagicMock, call, patch

import pytest

from canvas_sdk.clients.twillio.constants.date_operation import DateOperation
from canvas_sdk.clients.twillio.constants.http_method import HttpMethod
from canvas_sdk.clients.twillio.constants.message_direction import MessageDirection
from canvas_sdk.clients.twillio.constants.message_status import MessageStatus
from canvas_sdk.clients.twillio.libraries.sms_client import SmsClient
from canvas_sdk.clients.twillio.structures.capabilities import Capabilities
from canvas_sdk.clients.twillio.structures.media import Media
from canvas_sdk.clients.twillio.structures.message import Message
from canvas_sdk.clients.twillio.structures.phone import Phone
from canvas_sdk.clients.twillio.structures.request_failed import RequestFailed
from canvas_sdk.clients.twillio.structures.settings import Settings
from canvas_sdk.clients.twillio.structures.sms_mms import SmsMms
from canvas_sdk.clients.twillio.structures.structure import Structure


@dataclass(frozen=True)
class SimpleTestItem(Structure):
    """Simplified test structure for testing _valid_content_list pagination logic."""

    item_id: str
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create instance from dictionary."""
        return cls(item_id=data["item_id"], name=data["name"])

    def to_dict(self) -> dict:
        """Convert instance to dictionary."""
        return {"item_id": self.item_id, "name": self.name}


def test_init() -> None:
    """Test SmsClient.__init__ initializes settings and HTTP client correctly."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    assert client.settings == settings
    assert client.http._base_url == "https://api.twilio.com/2010-04-01/Accounts/AC123/"


def test_auth_header() -> None:
    """Test SmsClient._auth_header generates correct Basic auth header."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    result = client._auth_header()
    expected = {"Authorization": f"Basic {b64encode(b'test_key:test_secret').decode()}"}
    assert result == expected


def test_valid_content_list__single_page() -> None:
    """Test SmsClient._valid_content_list retrieves single page of data."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.side_effect = [
        {
            "items": [
                {
                    "item_id": "ID1",
                    "name": "Item One",
                }
            ],
            "next_page_uri": None,
        }
    ]

    mock_get = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "get", mock_get):
        result = list(client._valid_content_list("Items.json", "items", SimpleTestItem))

    expected = [SimpleTestItem(item_id="ID1", name="Item One")]
    assert result == expected

    exp_calls = [
        call("Items.json", headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="})
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = [call.json()]
    assert mock_response.mock_calls == exp_calls


def test_valid_content_list__multiple_pages() -> None:
    """Test SmsClient._valid_content_list retrieves multiple pages of data."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response_page1 = MagicMock()
    mock_response_page1.status_code = HTTPStatus.OK
    mock_response_page1.json.side_effect = [
        {
            "items": [
                {
                    "item_id": "ID1",
                    "name": "Item One",
                }
            ],
            "next_page_uri": "Items.json?Page=1",
        }
    ]

    mock_response_page2 = MagicMock()
    mock_response_page2.status_code = HTTPStatus.OK
    mock_response_page2.json.side_effect = [
        {
            "items": [
                {
                    "item_id": "ID2",
                    "name": "Item Two",
                }
            ],
            "next_page_uri": "Items.json?Page=2",
        }
    ]

    mock_response_page3 = MagicMock()
    mock_response_page3.status_code = HTTPStatus.OK
    mock_response_page3.json.side_effect = [
        {
            "items": [
                {
                    "item_id": "ID3",
                    "name": "Item Three",
                }
            ],
            "next_page_uri": None,
        }
    ]

    mock_get = MagicMock(
        side_effect=[mock_response_page1, mock_response_page2, mock_response_page3]
    )
    with patch.object(client.http, "get", mock_get):
        result = list(client._valid_content_list("Items.json", "items", SimpleTestItem))

    expected = [
        SimpleTestItem(item_id="ID1", name="Item One"),
        SimpleTestItem(item_id="ID2", name="Item Two"),
        SimpleTestItem(item_id="ID3", name="Item Three"),
    ]
    assert result == expected

    exp_calls = [
        call("Items.json", headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="}),
        call("Items.json?Page=1", headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="}),
        call("Items.json?Page=2", headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="}),
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = [call.json()]
    assert mock_response_page1.mock_calls == exp_calls
    assert mock_response_page2.mock_calls == exp_calls
    assert mock_response_page3.mock_calls == exp_calls


def test_valid_content_list__raises_request_failed() -> None:
    """Test SmsClient._valid_content_list raises RequestFailed on HTTP error."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    mock_response.content = b"Server error"

    mock_get = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "get", mock_get), pytest.raises(RequestFailed) as exc_info:
        list(client._valid_content_list("Items.json", "items", SimpleTestItem))

    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc_info.value.message == "Server error"

    exp_calls = [
        call("Items.json", headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="})
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = []
    assert mock_response.json.mock_calls == exp_calls


def test_valid_content_list__raises_request_failed_on_second_page() -> None:
    """Test SmsClient._valid_content_list raises RequestFailed when error occurs on subsequent page."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response_page1 = MagicMock()
    mock_response_page1.status_code = HTTPStatus.OK
    mock_response_page1.json.side_effect = [
        {
            "items": [
                {
                    "item_id": "ID1",
                    "name": "Item One",
                }
            ],
            "next_page_uri": "Items.json?Page=1",
        }
    ]

    mock_response_page2 = MagicMock()
    mock_response_page2.status_code = HTTPStatus.SERVICE_UNAVAILABLE
    mock_response_page2.content = b"Service temporarily unavailable"

    mock_get = MagicMock(side_effect=[mock_response_page1, mock_response_page2])
    with patch.object(client.http, "get", mock_get), pytest.raises(RequestFailed) as exc_info:
        list(client._valid_content_list("Items.json", "items", SimpleTestItem))

    assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert exc_info.value.message == "Service temporarily unavailable"

    exp_calls = [
        call("Items.json", headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="}),
        call("Items.json?Page=1", headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="}),
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = [call.json()]
    assert mock_response_page1.mock_calls == exp_calls

    exp_calls = []
    assert mock_response_page2.mock_calls == exp_calls


def test_account_phone_numbers() -> None:
    """Test SmsClient.account_phone_numbers retrieves paginated phone numbers."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    phone1 = Phone(
        account_sid="AC123",
        capabilities=Capabilities(fax=False, mms=True, sms=True, voice=True),
        date_created=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        date_updated=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        friendly_name="Phone 1",
        phone_number="+11234567890",
        sid="PN456",
        sms_fallback_method=HttpMethod.POST,
        sms_fallback_url="",
        sms_method=HttpMethod.POST,
        sms_url="",
        status_callback_method=HttpMethod.POST,
        status_callback="",
        status="in-use",
    )

    phone2 = Phone(
        account_sid="AC123",
        capabilities=Capabilities(fax=False, mms=False, sms=True, voice=False),
        date_created=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
        date_updated=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
        friendly_name="Phone 2",
        phone_number="+11234567891",
        sid="PN789",
        sms_fallback_method=HttpMethod.GET,
        sms_fallback_url="",
        sms_method=HttpMethod.GET,
        sms_url="",
        status_callback_method=HttpMethod.GET,
        status_callback="",
        status="in-use",
    )

    mock_valid_content_list = MagicMock(side_effect=[iter([phone1, phone2])])
    with patch.object(client, "_valid_content_list", mock_valid_content_list):
        phones = list(client.account_phone_numbers())

    expected = [phone1, phone2]
    assert phones == expected

    exp_calls = [call("IncomingPhoneNumbers.json", "incoming_phone_numbers", Phone)]
    assert mock_valid_content_list.mock_calls == exp_calls


def test_account_phone_number() -> None:
    """Test SmsClient.account_phone_number retrieves specific phone number."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.side_effect = [
        {
            "account_sid": "AC123",
            "capabilities": {"fax": False, "mms": True, "sms": True, "voice": True},
            "date_created": "Mon, 15 Dec 2025 10:30:00 +0000",
            "date_updated": "Mon, 15 Dec 2025 10:30:00 +0000",
            "friendly_name": "My Phone",
            "phone_number": "+11234567890",
            "sid": "PN456",
            "sms_fallback_method": "POST",
            "sms_fallback_url": "",
            "sms_method": "POST",
            "sms_url": "",
            "status_callback_method": "POST",
            "status_callback": "",
            "status": "in-use",
        }
    ]

    expected = Phone(
        account_sid="AC123",
        capabilities=Capabilities(fax=False, mms=True, sms=True, voice=True),
        date_created=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        date_updated=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        friendly_name="My Phone",
        phone_number="+11234567890",
        sid="PN456",
        sms_fallback_method=HttpMethod.POST,
        sms_fallback_url="",
        sms_method=HttpMethod.POST,
        sms_url="",
        status_callback_method=HttpMethod.POST,
        status_callback="",
        status="in-use",
    )

    mock_get = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "get", mock_get):
        result = client.account_phone_number("PN456")

    assert result == expected

    exp_calls = [
        call(
            "IncomingPhoneNumbers/PN456.json",
            headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="},
        )
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = [call.json()]
    assert mock_response.mock_calls == exp_calls


def test_account_phone_number__raises_request_failed() -> None:
    """Test SmsClient.account_phone_number raises RequestFailed on HTTP error."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.NOT_FOUND
    mock_response.content = b"Phone number not found"

    mock_get = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "get", mock_get), pytest.raises(RequestFailed) as exc_info:
        client.account_phone_number("PN999")

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.message == "Phone number not found"

    exp_calls = [
        call(
            "IncomingPhoneNumbers/PN999.json",
            headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="},
        )
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = []
    assert mock_response.json.mock_calls == exp_calls


def test_send_sms_mms() -> None:
    """Test SmsClient.send_sms_mms sends message and returns created Message."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    sms_mms = SmsMms(
        number_from="+11234567890",
        number_from_sid="PN456",
        number_to="+11234567891",
        message="Hello",
        media_url="",
        status_callback_url="",
    )

    # Mock account_phone_number to return capabilities
    mock_phone = Phone(
        account_sid="AC123",
        capabilities=Capabilities(fax=False, mms=True, sms=True, voice=True),
        date_created=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        date_updated=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        friendly_name="Test Phone",
        phone_number="+11234567890",
        sid="PN456",
        sms_fallback_method=HttpMethod.POST,
        sms_fallback_url="",
        sms_method=HttpMethod.POST,
        sms_url="",
        status_callback_method=HttpMethod.POST,
        status_callback="",
        status="in-use",
    )

    mock_post_response = MagicMock()
    mock_post_response.status_code = HTTPStatus.CREATED
    mock_post_response.json.side_effect = [
        {
            "sid": "SM123",
            "body": "Hello",
            "date_created": "Mon, 15 Dec 2025 10:30:00 +0000",
            "date_sent": "Mon, 15 Dec 2025 10:30:05 +0000",
            "date_updated": "Mon, 15 Dec 2025 10:30:10 +0000",
            "direction": "outbound-api",
            "from": "+11234567890",
            "to": "+11234567891",
            "price": "-0.00750",
            "price_unit": "USD",
            "error_code": None,
            "error_message": None,
            "uri": "/2010-04-01/Accounts/AC123/Messages/SM123",
            "num_media": 0,
            "num_segments": 1,
            "status": "sent",
            "subresource_uris": None,
        }
    ]

    expected = Message(
        sid="SM123",
        body="Hello",
        date_created=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        date_sent=datetime(2025, 12, 15, 10, 30, 5, tzinfo=UTC),
        date_updated=datetime(2025, 12, 15, 10, 30, 10, tzinfo=UTC),
        direction=MessageDirection.OUTBOUND_API,
        number_from="+11234567890",
        number_to="+11234567891",
        price="-0.00750",
        price_unit="USD",
        error_code=None,
        error_message=None,
        uri="/2010-04-01/Accounts/AC123/Messages/SM123",
        count_media=0,
        count_segments=1,
        status=MessageStatus.SENT,
        sub_resource_uris=None,
    )

    mock_account_phone_number = MagicMock(side_effect=[mock_phone])
    mock_post = MagicMock(side_effect=[mock_post_response])
    with (
        patch.object(client, "account_phone_number", mock_account_phone_number),
        patch.object(client.http, "post", mock_post),
    ):
        result = client.send_sms_mms(sms_mms)

    assert result == expected

    exp_calls = [call("PN456")]
    assert mock_account_phone_number.mock_calls == exp_calls

    exp_calls = [
        call(
            "Messages.json",
            data={"To": "+11234567891", "From": "+11234567890", "Body": "Hello"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ=",
            },
        )
    ]
    assert mock_post.mock_calls == exp_calls

    exp_calls = [call.json()]
    assert mock_post_response.mock_calls == exp_calls


def test_send_sms_mms__raises_request_failed() -> None:
    """Test SmsClient.send_sms_mms raises RequestFailed on HTTP error."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    sms_mms = SmsMms(
        number_from="+11234567890",
        number_from_sid="PN456",
        number_to="+11234567891",
        message="Hello",
        media_url="",
        status_callback_url="",
    )

    mock_phone = Phone(
        account_sid="AC123",
        capabilities=Capabilities(fax=False, mms=True, sms=True, voice=True),
        date_created=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        date_updated=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        friendly_name="Test Phone",
        phone_number="+11234567890",
        sid="PN456",
        sms_fallback_method=HttpMethod.POST,
        sms_fallback_url="",
        sms_method=HttpMethod.POST,
        sms_url="",
        status_callback_method=HttpMethod.POST,
        status_callback="",
        status="in-use",
    )

    mock_post_response = MagicMock()
    mock_post_response.status_code = HTTPStatus.BAD_REQUEST
    mock_post_response.content = b"Invalid phone number"

    mock_account_phone_number = MagicMock(side_effect=[mock_phone])
    mock_post = MagicMock(side_effect=[mock_post_response])
    with (
        patch.object(client, "account_phone_number", mock_account_phone_number),
        patch.object(client.http, "post", mock_post),
        pytest.raises(RequestFailed) as exc_info,
    ):
        client.send_sms_mms(sms_mms)

    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc_info.value.message == "Invalid phone number"

    exp_calls = [call("PN456")]
    assert mock_account_phone_number.mock_calls == exp_calls

    exp_calls = [
        call(
            "Messages.json",
            data={"To": "+11234567891", "From": "+11234567890", "Body": "Hello"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ=",
            },
        )
    ]
    assert mock_post.mock_calls == exp_calls

    exp_calls = []
    assert mock_post_response.json.mock_calls == exp_calls


def test_retrieve_sms() -> None:
    """Test SmsClient.retrieve_sms retrieves specific message."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.side_effect = [
        {
            "sid": "SM123",
            "body": "Test message",
            "date_created": "Mon, 15 Dec 2025 10:30:00 +0000",
            "date_sent": "Mon, 15 Dec 2025 10:30:05 +0000",
            "date_updated": "Mon, 15 Dec 2025 10:30:10 +0000",
            "direction": "outbound-api",
            "from": "+11234567890",
            "to": "+11234567891",
            "price": "-0.00750",
            "price_unit": "USD",
            "error_code": None,
            "error_message": None,
            "uri": "/2010-04-01/Accounts/AC123/Messages/SM123",
            "num_media": 0,
            "num_segments": 1,
            "status": "delivered",
            "subresource_uris": None,
        }
    ]

    expected = Message(
        sid="SM123",
        body="Test message",
        date_created=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        date_sent=datetime(2025, 12, 15, 10, 30, 5, tzinfo=UTC),
        date_updated=datetime(2025, 12, 15, 10, 30, 10, tzinfo=UTC),
        direction=MessageDirection.OUTBOUND_API,
        number_from="+11234567890",
        number_to="+11234567891",
        price="-0.00750",
        price_unit="USD",
        error_code=None,
        error_message=None,
        uri="/2010-04-01/Accounts/AC123/Messages/SM123",
        count_media=0,
        count_segments=1,
        status=MessageStatus.DELIVERED,
        sub_resource_uris=None,
    )

    mock_get = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "get", mock_get):
        result = client.retrieve_sms("SM123")

    assert result == expected

    exp_calls = [
        call("Messages/SM123.json", headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="})
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = [call.json()]
    assert mock_response.mock_calls == exp_calls


def test_retrieve_sms__raises_request_failed() -> None:
    """Test SmsClient.retrieve_sms raises RequestFailed on HTTP error."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.NOT_FOUND
    mock_response.content = b"Message not found"

    mock_get = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "get", mock_get), pytest.raises(RequestFailed) as exc_info:
        client.retrieve_sms("SM999")

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.message == "Message not found"

    exp_calls = [
        call(
            "Messages/SM999.json",
            headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="},
        )
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = []
    assert mock_response.json.mock_calls == exp_calls


def test_retrieve_all_sms() -> None:
    """Test SmsClient.retrieve_all_sms retrieves filtered messages."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    message1 = Message(
        sid="SM123",
        body="Message 1",
        date_created=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
        date_sent=datetime(2025, 12, 15, 10, 30, 5, tzinfo=UTC),
        date_updated=datetime(2025, 12, 15, 10, 30, 10, tzinfo=UTC),
        direction=MessageDirection.OUTBOUND_API,
        number_from="+11234567890",
        number_to="+11234567891",
        price="-0.00750",
        price_unit="USD",
        error_code=None,
        error_message=None,
        uri="/2010-04-01/Accounts/AC123/Messages/SM123",
        count_media=0,
        count_segments=1,
        status=MessageStatus.DELIVERED,
        sub_resource_uris=None,
    )

    mock_valid_content_list = MagicMock(side_effect=[iter([message1])])
    with patch.object(client, "_valid_content_list", mock_valid_content_list):
        messages = list(
            client.retrieve_all_sms(
                number_to="+11234567891",
                number_from="+11234567890",
                date_sent="2025-12-15",
                date_operation=DateOperation.ON_EXACTLY,
            )
        )

    expected = [message1]
    assert messages == expected

    exp_calls = [
        call(
            "Messages.json?DateSent=2025-12-15&To=%2B11234567891&From=%2B11234567890",
            "messages",
            Message,
        )
    ]
    assert mock_valid_content_list.mock_calls == exp_calls


@pytest.mark.parametrize(
    ("number_to", "number_from", "date_sent", "date_operation", "expected"),
    [
        pytest.param(
            "",
            "",
            "",
            DateOperation.ON_EXACTLY,
            "",
            id="all_empty",
        ),
        pytest.param(
            "+11234567890",
            "",
            "",
            DateOperation.ON_EXACTLY,
            "To=%2B11234567890",
            id="only_to",
        ),
        pytest.param(
            "",
            "+11234567891",
            "",
            DateOperation.ON_EXACTLY,
            "From=%2B11234567891",
            id="only_from",
        ),
        pytest.param(
            "",
            "",
            "2025-12-15",
            DateOperation.ON_EXACTLY,
            "DateSent=2025-12-15",
            id="date_on_exactly",
        ),
        pytest.param(
            "",
            "",
            "2025-12-15",
            DateOperation.ON_AND_AFTER,
            "DateSentAfter=2025-12-15",
            id="date_on_and_after",
        ),
        pytest.param(
            "",
            "",
            "2025-12-15",
            DateOperation.ON_AND_BEFORE,
            "DateSentBefore=2025-12-15",
            id="date_on_and_before",
        ),
        pytest.param(
            "+11234567890",
            "+11234567891",
            "2025-12-15",
            DateOperation.ON_EXACTLY,
            "DateSent=2025-12-15&To=%2B11234567890&From=%2B11234567891",
            id="all_fields",
        ),
    ],
)
def test__all_sms_query_params(
    number_to: str,
    number_from: str,
    date_sent: str,
    date_operation: DateOperation,
    expected: str,
) -> None:
    """Test SmsClient._all_sms_query_params builds correct query string."""
    result = SmsClient._all_sms_query_params(number_to, number_from, date_sent, date_operation)
    assert result == expected


def test_retrieve_media_list() -> None:
    """Test SmsClient.retrieve_media_list retrieves message media."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    media1 = Media(
        sid="ME123",
        content_type="image/jpeg",
        date_created=datetime(2025, 12, 15, 10, 30, 11, tzinfo=UTC),
        date_updated=datetime(2025, 12, 15, 10, 30, 15, tzinfo=UTC),
        parent_sid="MM456",
        uri="/2010-04-01/Accounts/AC789/Messages/MM456/Media/ME123",
    )

    mock_valid_content_list = MagicMock(side_effect=[iter([media1])])
    with patch.object(client, "_valid_content_list", mock_valid_content_list):
        media_list = list(client.retrieve_media_list("MM456"))

    expected = [media1]
    assert media_list == expected

    exp_calls = [call("Messages/MM456/Media.json", "media_list", Media)]
    assert mock_valid_content_list.mock_calls == exp_calls


def test_retrieve_raw_media() -> None:
    """Test SmsClient.retrieve_raw_media retrieves raw media content."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.content = b"fake_image_data"

    mock_get = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "get", mock_get):
        result = client.retrieve_raw_media("MM456", "ME123")

    assert result == b"fake_image_data"

    exp_calls = [
        call(
            "Messages/MM456/Media/ME123",
            headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="},
        )
    ]
    assert mock_get.mock_calls == exp_calls


def test_retrieve_raw_media__raises_request_failed() -> None:
    """Test SmsClient.retrieve_raw_media raises RequestFailed on HTTP error."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.NOT_FOUND
    mock_response.content = b"Media not found"

    mock_get = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "get", mock_get), pytest.raises(RequestFailed) as exc_info:
        client.retrieve_raw_media("MM456", "ME999")

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.message == "Media not found"

    exp_calls = [
        call(
            "Messages/MM456/Media/ME999",
            headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="},
        )
    ]
    assert mock_get.mock_calls == exp_calls


def test_delete_sms() -> None:
    """Test SmsClient.delete_sms deletes message successfully."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.NO_CONTENT

    mock_delete = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "delete", mock_delete):
        result = client.delete_sms("SM123")

    assert result is True

    exp_calls = [
        call(
            "Messages/SM123.json",
            headers={
                "Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ=",
            },
        )
    ]
    assert mock_delete.mock_calls == exp_calls


def test_delete_sms__raises_request_failed() -> None:
    """Test SmsClient.delete_sms raises RequestFailed on HTTP error."""
    settings = Settings(account_sid="AC123", key="test_key", secret="test_secret")
    client = SmsClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.NOT_FOUND
    mock_response.content = b"Message not found"

    mock_delete = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "delete", mock_delete), pytest.raises(RequestFailed) as exc_info:
        client.delete_sms("SM999")

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.message == "Message not found"

    exp_calls = [
        call(
            "Messages/SM999.json",
            headers={"Authorization": "Basic dGVzdF9rZXk6dGVzdF9zZWNyZXQ="},
        )
    ]
    assert mock_delete.mock_calls == exp_calls
