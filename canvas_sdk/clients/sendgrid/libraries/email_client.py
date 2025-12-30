from collections.abc import Iterator
from http import HTTPStatus
from typing import TypeVar

from requests import Response

from canvas_sdk.clients.sendgrid.constants.recipient_type import RecipientType
from canvas_sdk.clients.sendgrid.structures.email import Email
from canvas_sdk.clients.sendgrid.structures.event_webhook import EventWebhook
from canvas_sdk.clients.sendgrid.structures.event_webhook_record import EventWebhookRecord
from canvas_sdk.clients.sendgrid.structures.logged_email_criteria import LoggedEmailCriteria
from canvas_sdk.clients.sendgrid.structures.parse_setting import ParseSetting
from canvas_sdk.clients.sendgrid.structures.request_failed import RequestFailed
from canvas_sdk.clients.sendgrid.structures.sent_email import SentEmail
from canvas_sdk.clients.sendgrid.structures.sent_email_detailed import SentEmailDetailed
from canvas_sdk.clients.sendgrid.structures.settings import Settings
from canvas_sdk.clients.sendgrid.structures.structure import Structure
from canvas_sdk.utils import Http

Data = TypeVar("Data", bound=Structure)


class EmailClient:
    """Client for interacting with SendGrid API."""

    def __init__(self, settings: Settings):
        """Initialize EmailClient with API settings."""
        self.settings = settings
        self.http = Http("https://api.sendgrid.com")

    def _auth_header(self) -> dict:
        """Generate authorization header with API key."""
        return {
            "Authorization": f"Bearer {self.settings.key}",
        }

    @classmethod
    def _valid_content_bool(cls, request: Response, status: HTTPStatus) -> bool:
        """Validate response status and return True on success.

        Args:
            request: The HTTP response object
            status: Expected status code

        Returns:
            True if status code matches

        Raises:
            RequestFailed: If status code does not match expected
        """
        if request.status_code == status:
            return True
        raise RequestFailed(status_code=request.status_code, message=request.content.decode())

    @classmethod
    def _valid_content(
        cls,
        request: Response,
        statuses: list[HTTPStatus],
        returned: type[Data],
    ) -> Data:
        """Validate response status and parse single object.

        Args:
            request: The HTTP response object
            statuses: List of acceptable status codes
            returned: Structure class to parse response data into

        Returns:
            Parsed object of the specified type

        Raises:
            RequestFailed: If status code is not in acceptable list
        """
        if request.status_code in statuses:
            return returned.from_dict(request.json())
        raise RequestFailed(status_code=request.status_code, message=request.content.decode())

    @classmethod
    def _valid_content_list(
        cls,
        request: Response,
        status: HTTPStatus,
        key: str,
        returned: type[Data],
    ) -> Iterator[Data]:
        """Validate response status and yield parsed objects from list.

        Args:
            request: The HTTP response object
            status: Expected status code
            key: JSON key to extract list from response
            returned: Structure class to parse each item into

        Yields:
            Parsed objects of the specified type

        Raises:
            RequestFailed: If status code does not match expected
        """
        if request.status_code != status:
            raise RequestFailed(status_code=request.status_code, message=request.content.decode())
        for item in request.json()[key]:
            yield returned.from_dict(item)

    def simple_send(self, email: Email) -> bool:
        """Send an email using simplified interface.

        This method provides an easy way to send emails without complexity requirements.
        It uses the prepared_send method internally, which provides support for
        advanced and complex email-sending workflows.

        Note: SendGrid enforces the presence of at least one email in the `to` section.
        """
        per_recipient_type = {
            "to": RecipientType.TO,
            "cc": RecipientType.CC,
            "bcc": RecipientType.BCC,
        }
        data = {
            "from": email.sender.to_dict(),
            "reply_to_list": [r.to_dict() for r in email.reply_tos],
            "subject": email.subject,
            "content": [b.to_dict() for b in email.bodies],
            "send_at": email.send_at,
            "personalizations": [
                {
                    key: listed
                    for key, recipient_type in per_recipient_type.items()
                    if (
                        listed := [
                            r.address.to_dict()
                            for r in email.recipients
                            if r.type == recipient_type
                        ]
                    )
                }
            ],
            "attachments": [a.to_dict() for a in email.attachments],
        }
        return self.prepared_send(data)

    def prepared_send(self, data: dict) -> bool:
        """Send an email using prepared data dictionary.

        The data dictionary must follow SendGrid's schema:
        https://www.twilio.com/docs/sendgrid/api-reference/mail-send/mail-send#request-body
        """
        url = "/v3/mail/send"
        headers = {"Content-Type": "application/json"} | self._auth_header()
        request = self.http.post(url, json=data, headers=headers)
        return self._valid_content_bool(request, HTTPStatus.ACCEPTED)

    def logged_emails(self, criteria: LoggedEmailCriteria, up_to: int) -> Iterator[SentEmail]:
        """Retrieve logged emails matching search criteria."""
        url = "/v3/logs"
        headers = {"Content-Type": "application/json"} | self._auth_header()
        data = {
            "query": criteria.to_str(),
            "limit": up_to,
        }
        request = self.http.post(url, json=data, headers=headers)
        yield from self._valid_content_list(request, HTTPStatus.OK, "messages", SentEmail)

    def logged_email(self, message_id: str) -> SentEmailDetailed:
        """Retrieve detailed information for a specific email by message ID."""
        url = f"/v3/logs/{message_id}"
        request = self.http.get(url, headers=self._auth_header())
        return self._valid_content(request, [HTTPStatus.OK], SentEmailDetailed)

    # incoming emails:
    # - SendGrid UI  : https://app.sendgrid.com/settings/parse
    # - documentation: https://www.twilio.com/docs/sendgrid/for-developers/parsing-email/inbound-email
    def parser_setting_add(self, setting: ParseSetting) -> ParseSetting:
        """Add a new inbound parse webhook setting."""
        url = "/v3/user/webhooks/parse/settings"
        headers = {"Content-Type": "application/json"} | self._auth_header()
        request = self.http.post(url, json=setting.to_dict(), headers=headers)
        # discrepancy between the doc and the reality:
        # - 201 according to: https://www.twilio.com/docs/sendgrid/api-reference/settings-inbound-parse/create-a-parse-setting#responses
        # - 200 based on real usages
        return self._valid_content(request, [HTTPStatus.OK, HTTPStatus.CREATED], ParseSetting)

    def parser_setting_delete(self, hostname: str) -> bool:
        """Delete an inbound parse webhook setting by hostname."""
        url = f"/v3/user/webhooks/parse/settings/{hostname}"
        request = self.http.delete(url, headers=self._auth_header())
        return self._valid_content_bool(request, HTTPStatus.NO_CONTENT)

    def parser_setting_get(self, hostname: str) -> ParseSetting:
        """Retrieve an inbound parse webhook setting by hostname."""
        url = f"/v3/user/webhooks/parse/settings/{hostname}"
        request = self.http.get(url, headers=self._auth_header())
        return self._valid_content(request, [HTTPStatus.OK], ParseSetting)

    def parser_setting_list(self) -> Iterator[ParseSetting]:
        """List all inbound parse webhook settings."""
        url = "/v3/user/webhooks/parse/settings"
        request = self.http.get(url, headers=self._auth_header())
        yield from self._valid_content_list(request, HTTPStatus.OK, "result", ParseSetting)

    # sent email statuses:
    # - SendGrid UI  : https://app.sendgrid.com/settings/mail_settings/webhook_settings
    # - documentation: https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event
    def event_webhook_add(self, event: EventWebhook) -> EventWebhookRecord:
        """Add a new event webhook for email status notifications."""
        url = "/v3/user/webhooks/event/settings"
        headers = {"Content-Type": "application/json"} | self._auth_header()
        request = self.http.post(url, json=event.to_dict(), headers=headers)
        return self._valid_content(request, [HTTPStatus.CREATED], EventWebhookRecord)

    def event_webhook_sign(self, event_webhook_id: str, enabled: bool) -> str:
        """Enable or disable webhook signature verification and return public key."""
        url = f"/v3/user/webhooks/event/settings/signed/{event_webhook_id}"
        headers = {"Content-Type": "application/json"} | self._auth_header()
        request = self.http.patch(url, json={"enabled": enabled}, headers=headers)
        if request.status_code == HTTPStatus.OK:
            return request.json().get("public_key") or ""
        raise RequestFailed(status_code=request.status_code, message=request.content.decode())

    def event_webhook_delete(self, event_webhook_id: str) -> bool:
        """Delete an event webhook by ID."""
        url = f"/v3/user/webhooks/event/settings/{event_webhook_id}"
        request = self.http.delete(url, headers=self._auth_header())
        return self._valid_content_bool(request, HTTPStatus.NO_CONTENT)

    def event_webhook_get(self, event_webhook_id: str) -> EventWebhookRecord:
        """Retrieve an event webhook by ID."""
        url = f"/v3/user/webhooks/event/settings/{event_webhook_id}"
        request = self.http.get(url, headers=self._auth_header())
        return self._valid_content(request, [HTTPStatus.OK], EventWebhookRecord)

    def event_webhook_list(self) -> Iterator[EventWebhookRecord]:
        """List all event webhooks."""
        url = "/v3/user/webhooks/event/settings/all"
        request = self.http.get(url, headers=self._auth_header())
        yield from self._valid_content_list(request, HTTPStatus.OK, "webhooks", EventWebhookRecord)


__exports__ = ()
