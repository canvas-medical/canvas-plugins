from datetime import datetime
from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest

from canvas_sdk.clients.sendgrid.constants.attachment_disposition import AttachmentDisposition
from canvas_sdk.clients.sendgrid.constants.recipient_type import RecipientType
from canvas_sdk.clients.sendgrid.constants.status_email import StatusEmail
from canvas_sdk.clients.sendgrid.libraries.email_client import EmailClient
from canvas_sdk.clients.sendgrid.structures.address import Address
from canvas_sdk.clients.sendgrid.structures.attachment import Attachment
from canvas_sdk.clients.sendgrid.structures.body_content import BodyContent
from canvas_sdk.clients.sendgrid.structures.email import Email
from canvas_sdk.clients.sendgrid.structures.event_webhook import EventWebhook
from canvas_sdk.clients.sendgrid.structures.event_webhook_record import EventWebhookRecord
from canvas_sdk.clients.sendgrid.structures.logged_email_criteria import LoggedEmailCriteria
from canvas_sdk.clients.sendgrid.structures.parse_setting import ParseSetting
from canvas_sdk.clients.sendgrid.structures.recipient import Recipient
from canvas_sdk.clients.sendgrid.structures.request_failed import RequestFailed
from canvas_sdk.clients.sendgrid.structures.sent_email import SentEmail
from canvas_sdk.clients.sendgrid.structures.sent_email_detailed import SentEmailDetailed
from canvas_sdk.clients.sendgrid.structures.settings import Settings


def test_init() -> None:
    """Test EmailClient.__init__ initializes settings and HTTP client correctly."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    assert client.settings == settings
    assert client.http._base_url == "https://api.sendgrid.com"


def test_auth_header() -> None:
    """Test EmailClient._auth_header generates correct Bearer auth header."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    result = client._auth_header()
    expected = {"Authorization": "Bearer test_api_key"}
    assert result == expected


def test_valid_content_bool() -> None:
    """Test EmailClient._valid_content_bool returns True on matching status."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.ACCEPTED

    result = EmailClient._valid_content_bool(mock_response, HTTPStatus.ACCEPTED)

    assert result is True

    exp_calls: list = []
    assert mock_response.mock_calls == exp_calls


def test_valid_content_bool__raises_request_failed() -> None:
    """Test EmailClient._valid_content_bool raises RequestFailed on mismatched status."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.BAD_REQUEST
    mock_response.content.decode.side_effect = ["Invalid request"]

    with pytest.raises(RequestFailed) as exc_info:
        EmailClient._valid_content_bool(mock_response, HTTPStatus.OK)

    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc_info.value.message == "Invalid request"

    exp_calls = [call.content.decode()]
    assert mock_response.mock_calls == exp_calls


def test_valid_content() -> None:
    """Test EmailClient._valid_content parses single object on matching status."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.side_effect = [
        {
            "url": "https://example.com/parse",
            "hostname": "mail.example.com",
            "spam_check": True,
            "send_raw": False,
        }
    ]

    result = EmailClient._valid_content(mock_response, [HTTPStatus.OK], ParseSetting)

    assert isinstance(result, ParseSetting)
    assert result.url == "https://example.com/parse"
    assert result.hostname == "mail.example.com"
    assert result.spam_check is True
    assert result.send_raw is False

    exp_calls = [call.json()]
    assert mock_response.mock_calls == exp_calls


def test_valid_content__with_multiple_statuses() -> None:
    """Test EmailClient._valid_content accepts multiple valid status codes."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.CREATED
    mock_response.json.side_effect = [
        {
            "url": "https://example.com/parse",
            "hostname": "mail.example.com",
            "spam_check": False,
            "send_raw": True,
        }
    ]

    result = EmailClient._valid_content(
        mock_response, [HTTPStatus.OK, HTTPStatus.CREATED], ParseSetting
    )

    assert isinstance(result, ParseSetting)
    assert result.url == "https://example.com/parse"

    exp_calls = [call.json()]
    assert mock_response.mock_calls == exp_calls


def test_valid_content__raises_request_failed() -> None:
    """Test EmailClient._valid_content raises RequestFailed on mismatched status."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.NOT_FOUND
    mock_response.content.decode.side_effect = ["Not found"]

    with pytest.raises(RequestFailed) as exc_info:
        EmailClient._valid_content(mock_response, [HTTPStatus.OK], ParseSetting)

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.message == "Not found"

    exp_calls = [call.content.decode()]
    assert mock_response.mock_calls == exp_calls


def test_valid_content_list() -> None:
    """Test EmailClient._valid_content_list yields parsed objects from list."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.side_effect = [
        {
            "result": [
                {
                    "url": "https://example.com/parse1",
                    "hostname": "mail1.example.com",
                    "spam_check": True,
                    "send_raw": False,
                },
                {
                    "url": "https://example.com/parse2",
                    "hostname": "mail2.example.com",
                    "spam_check": False,
                    "send_raw": True,
                },
            ]
        }
    ]

    result = list(
        EmailClient._valid_content_list(mock_response, HTTPStatus.OK, "result", ParseSetting)
    )

    assert len(result) == 2
    assert isinstance(result[0], ParseSetting)
    assert result[0].url == "https://example.com/parse1"
    assert result[0].hostname == "mail1.example.com"
    assert isinstance(result[1], ParseSetting)
    assert result[1].url == "https://example.com/parse2"
    assert result[1].hostname == "mail2.example.com"

    exp_calls = [call.json()]
    assert mock_response.mock_calls == exp_calls


def test_valid_content_list__raises_request_failed() -> None:
    """Test EmailClient._valid_content_list raises RequestFailed on mismatched status."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    mock_response.content.decode.side_effect = ["Server error"]

    with pytest.raises(RequestFailed) as exc_info:
        list(EmailClient._valid_content_list(mock_response, HTTPStatus.OK, "result", ParseSetting))

    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc_info.value.message == "Server error"

    exp_calls = [call.content.decode()]
    assert mock_response.mock_calls == exp_calls


@pytest.mark.parametrize(
    ("email", "expected_data"),
    [
        pytest.param(
            Email(
                sender=Address(email="sender@example.com", name="Sender"),
                reply_tos=[Address(email="reply@example.com", name="Reply")],
                recipients=[
                    Recipient(
                        address=Address(email="to@example.com", name="To"), type=RecipientType.TO
                    ),
                    Recipient(
                        address=Address(email="cc@example.com", name="CC"), type=RecipientType.CC
                    ),
                ],
                subject="Test Subject",
                bodies=[BodyContent(type="text/plain", value="Test body")],
                attachments=[],
                send_at=0,
            ),
            {
                "from": {"email": "sender@example.com", "name": "Sender"},
                "reply_to_list": [{"email": "reply@example.com", "name": "Reply"}],
                "subject": "Test Subject",
                "content": [{"type": "text/plain", "value": "Test body"}],
                "send_at": 0,
                "personalizations": [
                    {
                        "to": [{"email": "to@example.com", "name": "To"}],
                        "cc": [{"email": "cc@example.com", "name": "CC"}],
                    }
                ],
            },
            id="without_attachments",
        ),
        pytest.param(
            Email(
                sender=Address(email="sender@example.com", name="Sender"),
                reply_tos=[],
                recipients=[
                    Recipient(
                        address=Address(email="to@example.com", name="To"), type=RecipientType.TO
                    )
                ],
                subject="Test Subject",
                bodies=[BodyContent(type="text/html", value="<p>Test body</p>")],
                attachments=[
                    Attachment(
                        content_id="img123",
                        content="aGVsbG8gd29ybGQ=",
                        type="image/png",
                        filename="test.png",
                        disposition=AttachmentDisposition.INLINE,
                    )
                ],
                send_at=1765794600,
            ),
            {
                "from": {"email": "sender@example.com", "name": "Sender"},
                "reply_to_list": [],
                "subject": "Test Subject",
                "content": [{"type": "text/html", "value": "<p>Test body</p>"}],
                "send_at": 1765794600,
                "personalizations": [
                    {
                        "to": [{"email": "to@example.com", "name": "To"}],
                    }
                ],
                "attachments": [
                    {
                        "content_id": "img123",
                        "content": "aGVsbG8gd29ybGQ=",
                        "type": "image/png",
                        "filename": "test.png",
                        "disposition": "inline",
                    }
                ],
            },
            id="with_attachments",
        ),
    ],
)
def test_simple_send(email: Email, expected_data: dict) -> None:
    """Test EmailClient.simple_send sends email successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_prepared_send = MagicMock(side_effect=[True])
    with patch.object(client, "prepared_send", mock_prepared_send):
        result = client.simple_send(email)

    assert result is True

    exp_calls = [call(expected_data)]
    assert mock_prepared_send.mock_calls == exp_calls


@pytest.mark.parametrize(
    ("webhook_id", "enabled", "public_key", "expected_result"),
    [
        pytest.param("WH123", True, "pubkey123", "pubkey123", id="enabled"),
        pytest.param("WH456", False, None, "", id="disabled"),
    ],
)
def test_event_webhook_sign(
    webhook_id: str, enabled: bool, public_key: str | None, expected_result: str
) -> None:
    """Test EmailClient.event_webhook_sign enables or disables signature for webhook."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.side_effect = [{"public_key": public_key}]

    mock_patch = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "patch", mock_patch):
        result = client.event_webhook_sign(webhook_id, enabled)

    assert result == expected_result

    exp_calls = [
        call(
            f"/v3/user/webhooks/event/settings/signed/{webhook_id}",
            json={"enabled": enabled},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_api_key",
            },
        )
    ]
    assert mock_patch.mock_calls == exp_calls

    exp_calls = [call.json()]
    assert mock_response.mock_calls == exp_calls


def test_event_webhook_sign__raises_request_failed() -> None:
    """Test EmailClient.event_webhook_sign raises RequestFailed on HTTP error."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.NOT_FOUND
    mock_response.content = b"Webhook not found"

    mock_patch = MagicMock(side_effect=[mock_response])
    with patch.object(client.http, "patch", mock_patch), pytest.raises(RequestFailed) as exc_info:
        client.event_webhook_sign("WH999", True)

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.message == "Webhook not found"

    exp_calls = [
        call(
            "/v3/user/webhooks/event/settings/signed/WH999",
            json={"enabled": True},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_api_key",
            },
        )
    ]
    assert mock_patch.mock_calls == exp_calls

    exp_calls = []
    assert mock_response.json.mock_calls == exp_calls


def test_prepared_send() -> None:
    """Test EmailClient.prepared_send sends email successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_post = MagicMock(side_effect=[mock_response])

    mock_valid_content_bool = MagicMock(side_effect=[True])

    data = {"from": {"email": "test@example.com"}}

    with (
        patch.object(client.http, "post", mock_post),
        patch.object(EmailClient, "_valid_content_bool", mock_valid_content_bool),
    ):
        result = client.prepared_send(data)

    assert result is True

    exp_calls = [
        call(
            "/v3/mail/send",
            json=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_api_key",
            },
        )
    ]
    assert mock_post.mock_calls == exp_calls

    exp_calls = [call(mock_response, HTTPStatus.ACCEPTED)]
    assert mock_valid_content_bool.mock_calls == exp_calls


def test_logged_emails() -> None:
    """Test EmailClient.logged_emails retrieves logged emails successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_post = MagicMock(side_effect=[mock_response])

    sent_email = SentEmail(
        from_email="from@example.com",
        message_id="MSG123",
        subject="Test Subject",
        to_email="to@example.com",
        reason="",
        status=StatusEmail.DELIVERED,
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    mock_valid_content_list = MagicMock(side_effect=[[sent_email]])

    criteria = LoggedEmailCriteria(
        message_id="MSG123",
        subject="",
        to_email="",
        reason="",
        status=[],
        message_created_at=[],
    )

    with (
        patch.object(client.http, "post", mock_post),
        patch.object(EmailClient, "_valid_content_list", mock_valid_content_list),
    ):
        result = list(client.logged_emails(criteria, 10))

    assert result == [sent_email]

    exp_calls = [
        call(
            "/v3/logs",
            json={"query": 'sg_message_id="MSG123"', "limit": 10},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_api_key",
            },
        )
    ]
    assert mock_post.mock_calls == exp_calls

    exp_calls = [call(mock_response, HTTPStatus.OK, "messages", SentEmail)]
    assert mock_valid_content_list.mock_calls == exp_calls


def test_logged_email() -> None:
    """Test EmailClient.logged_email retrieves detailed email successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_get = MagicMock(side_effect=[mock_response])

    sent_email_detailed = SentEmailDetailed(
        from_email="from@example.com",
        message_id="MSG123",
        subject="Test Subject",
        to_email="to@example.com",
        status=StatusEmail.DELIVERED,
        events=[],
    )
    mock_valid_content = MagicMock(side_effect=[sent_email_detailed])

    with (
        patch.object(client.http, "get", mock_get),
        patch.object(EmailClient, "_valid_content", mock_valid_content),
    ):
        result = client.logged_email("MSG123")

    assert result == sent_email_detailed

    exp_calls = [call("/v3/logs/MSG123", headers={"Authorization": "Bearer test_api_key"})]
    assert mock_get.mock_calls == exp_calls

    exp_calls = [call(mock_response, [HTTPStatus.OK], SentEmailDetailed)]
    assert mock_valid_content.mock_calls == exp_calls


def test_parser_setting_add() -> None:
    """Test EmailClient.parser_setting_add creates parse setting successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_post = MagicMock(side_effect=[mock_response])

    parse_setting = ParseSetting(
        url="https://example.com/parse",
        hostname="mail.example.com",
        spam_check=True,
        send_raw=False,
    )
    mock_valid_content = MagicMock(side_effect=[parse_setting])

    with (
        patch.object(client.http, "post", mock_post),
        patch.object(EmailClient, "_valid_content", mock_valid_content),
    ):
        result = client.parser_setting_add(parse_setting)

    assert result == parse_setting

    exp_calls = [
        call(
            "/v3/user/webhooks/parse/settings",
            json={
                "url": "https://example.com/parse",
                "hostname": "mail.example.com",
                "spam_check": True,
                "send_raw": False,
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_api_key",
            },
        )
    ]
    assert mock_post.mock_calls == exp_calls

    exp_calls = [call(mock_response, [HTTPStatus.OK, HTTPStatus.CREATED], ParseSetting)]
    assert mock_valid_content.mock_calls == exp_calls


def test_parser_setting_delete() -> None:
    """Test EmailClient.parser_setting_delete deletes parse setting successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_delete = MagicMock(side_effect=[mock_response])

    mock_valid_content_bool = MagicMock(side_effect=[True])

    with (
        patch.object(client.http, "delete", mock_delete),
        patch.object(EmailClient, "_valid_content_bool", mock_valid_content_bool),
    ):
        result = client.parser_setting_delete("mail.example.com")

    assert result is True

    exp_calls = [
        call(
            "/v3/user/webhooks/parse/settings/mail.example.com",
            headers={"Authorization": "Bearer test_api_key"},
        )
    ]
    assert mock_delete.mock_calls == exp_calls

    exp_calls = [call(mock_response, HTTPStatus.NO_CONTENT)]
    assert mock_valid_content_bool.mock_calls == exp_calls


def test_parser_setting_get() -> None:
    """Test EmailClient.parser_setting_get retrieves parse setting successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_get = MagicMock(side_effect=[mock_response])

    parse_setting = ParseSetting(
        url="https://example.com/parse",
        hostname="mail.example.com",
        spam_check=True,
        send_raw=False,
    )
    mock_valid_content = MagicMock(side_effect=[parse_setting])

    with (
        patch.object(client.http, "get", mock_get),
        patch.object(EmailClient, "_valid_content", mock_valid_content),
    ):
        result = client.parser_setting_get("mail.example.com")

    assert result == parse_setting

    exp_calls = [
        call(
            "/v3/user/webhooks/parse/settings/mail.example.com",
            headers={"Authorization": "Bearer test_api_key"},
        )
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = [call(mock_response, [HTTPStatus.OK], ParseSetting)]
    assert mock_valid_content.mock_calls == exp_calls


def test_parser_setting_list() -> None:
    """Test EmailClient.parser_setting_list lists all parse settings successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_get = MagicMock(side_effect=[mock_response])

    parse_setting = ParseSetting(
        url="https://example.com/parse",
        hostname="mail.example.com",
        spam_check=True,
        send_raw=False,
    )
    mock_valid_content_list = MagicMock(side_effect=[[parse_setting]])

    with (
        patch.object(client.http, "get", mock_get),
        patch.object(EmailClient, "_valid_content_list", mock_valid_content_list),
    ):
        result = list(client.parser_setting_list())

    assert result == [parse_setting]

    exp_calls = [
        call(
            "/v3/user/webhooks/parse/settings",
            headers={"Authorization": "Bearer test_api_key"},
        )
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = [call(mock_response, HTTPStatus.OK, "result", ParseSetting)]
    assert mock_valid_content_list.mock_calls == exp_calls


def test_event_webhook_add() -> None:
    """Test EmailClient.event_webhook_add creates event webhook successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_post = MagicMock(side_effect=[mock_response])

    event_webhook = EventWebhook(
        enabled=True,
        url="https://example.com/webhook",
        group_resubscribe=False,
        group_unsubscribe=False,
        delivered=True,
        spam_report=False,
        bounce=True,
        unsubscribe=False,
        dropped=False,
        open=False,
        click=False,
        processed=False,
        friendly_name="Test Webhook",
    )
    event_webhook_record = EventWebhookRecord(
        id="WH123",
        public_key="",
        enabled=True,
        url="https://example.com/webhook",
        group_resubscribe=False,
        group_unsubscribe=False,
        delivered=True,
        spam_report=False,
        bounce=True,
        unsubscribe=False,
        dropped=False,
        open=False,
        click=False,
        processed=False,
        friendly_name="Test Webhook",
        created_date=datetime(2025, 1, 1, 12, 0, 0),
        updated_date=datetime(2025, 1, 1, 12, 0, 0),
    )
    mock_valid_content = MagicMock(side_effect=[event_webhook_record])

    with (
        patch.object(client.http, "post", mock_post),
        patch.object(EmailClient, "_valid_content", mock_valid_content),
    ):
        result = client.event_webhook_add(event_webhook)

    assert result == event_webhook_record

    exp_calls = [
        call(
            "/v3/user/webhooks/event/settings",
            json={
                "enabled": True,
                "url": "https://example.com/webhook",
                "group_resubscribe": False,
                "group_unsubscribe": False,
                "delivered": True,
                "spam_report": False,
                "bounce": True,
                "unsubscribe": False,
                "dropped": False,
                "open": False,
                "click": False,
                "processed": False,
                "friendly_name": "Test Webhook",
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_api_key",
            },
        )
    ]
    assert mock_post.mock_calls == exp_calls

    exp_calls = [call(mock_response, [HTTPStatus.CREATED], EventWebhookRecord)]
    assert mock_valid_content.mock_calls == exp_calls


def test_event_webhook_delete() -> None:
    """Test EmailClient.event_webhook_delete deletes event webhook successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_delete = MagicMock(side_effect=[mock_response])

    mock_valid_content_bool = MagicMock(side_effect=[True])

    with (
        patch.object(client.http, "delete", mock_delete),
        patch.object(EmailClient, "_valid_content_bool", mock_valid_content_bool),
    ):
        result = client.event_webhook_delete("WH123")

    assert result is True

    exp_calls = [
        call(
            "/v3/user/webhooks/event/settings/WH123",
            headers={"Authorization": "Bearer test_api_key"},
        )
    ]
    assert mock_delete.mock_calls == exp_calls

    exp_calls = [call(mock_response, HTTPStatus.NO_CONTENT)]
    assert mock_valid_content_bool.mock_calls == exp_calls


def test_event_webhook_get() -> None:
    """Test EmailClient.event_webhook_get retrieves event webhook successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_get = MagicMock(side_effect=[mock_response])

    event_webhook_record = EventWebhookRecord(
        id="WH123",
        public_key="pubkey123",
        enabled=True,
        url="https://example.com/webhook",
        group_resubscribe=False,
        group_unsubscribe=False,
        delivered=True,
        spam_report=False,
        bounce=True,
        unsubscribe=False,
        dropped=False,
        open=False,
        click=False,
        processed=False,
        friendly_name="Test Webhook",
        created_date=datetime(2025, 1, 1, 12, 0, 0),
        updated_date=datetime(2025, 1, 1, 12, 0, 0),
    )
    mock_valid_content = MagicMock(side_effect=[event_webhook_record])

    with (
        patch.object(client.http, "get", mock_get),
        patch.object(EmailClient, "_valid_content", mock_valid_content),
    ):
        result = client.event_webhook_get("WH123")

    assert result == event_webhook_record

    exp_calls = [
        call(
            "/v3/user/webhooks/event/settings/WH123",
            headers={"Authorization": "Bearer test_api_key"},
        )
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = [call(mock_response, [HTTPStatus.OK], EventWebhookRecord)]
    assert mock_valid_content.mock_calls == exp_calls


def test_event_webhook_list() -> None:
    """Test EmailClient.event_webhook_list lists all event webhooks successfully."""
    settings = Settings(key="test_api_key")
    client = EmailClient(settings)

    mock_response = SimpleNamespace()
    mock_get = MagicMock(side_effect=[mock_response])

    event_webhook_record = EventWebhookRecord(
        id="WH123",
        public_key="pubkey123",
        enabled=True,
        url="https://example.com/webhook",
        group_resubscribe=False,
        group_unsubscribe=False,
        delivered=True,
        spam_report=False,
        bounce=True,
        unsubscribe=False,
        dropped=False,
        open=False,
        click=False,
        processed=False,
        friendly_name="Test Webhook",
        created_date=datetime(2025, 1, 1, 12, 0, 0),
        updated_date=datetime(2025, 1, 1, 12, 0, 0),
    )
    mock_valid_content_list = MagicMock(side_effect=[[event_webhook_record]])

    with (
        patch.object(client.http, "get", mock_get),
        patch.object(EmailClient, "_valid_content_list", mock_valid_content_list),
    ):
        result = list(client.event_webhook_list())

    assert result == [event_webhook_record]

    exp_calls = [
        call(
            "/v3/user/webhooks/event/settings/all",
            headers={"Authorization": "Bearer test_api_key"},
        )
    ]
    assert mock_get.mock_calls == exp_calls

    exp_calls = [call(mock_response, HTTPStatus.OK, "webhooks", EventWebhookRecord)]
    assert mock_valid_content_list.mock_calls == exp_calls
