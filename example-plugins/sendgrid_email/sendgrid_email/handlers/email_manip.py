from datetime import UTC, datetime, timedelta
from http import HTTPStatus

from canvas_sdk.caching.plugins import get_cache
from canvas_sdk.clients.sendgrid.constants import CriterionOperation, RecipientType
from canvas_sdk.clients.sendgrid.libraries import EmailClient
from canvas_sdk.clients.sendgrid.structures import (
    Address,
    Attachment,
    BodyContent,
    CriterionDatetime,
    Email,
    EmailEvent,
    EventWebhook,
    LoggedEmailCriteria,
    ParsedEmail,
    ParseSetting,
    Recipient,
    RequestFailed,
    Settings,
)
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPI, api
from logger import log

from ..constants.constants import Constants


class EmailManip(SimpleAPI):
    """API handler for Sendgrid email operations.

    Provides endpoints for sending emails, retrieving sent emails, managing webhooks,
    and handling inbound/outbound email events through the Sendgrid API.
    """

    PREFIX = None

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate the API request.

        Args:
            credentials: The credentials provided for authentication.

        Returns:
            bool: Always returns True for simplicity. TODO: implement proper authentication.
        """
        return True

    def _sendgrid_client(self) -> EmailClient:
        """Create and return a configured Sendgrid email client.

        Returns:
            EmailClient: An initialized Sendgrid client with API credentials.
        """
        settings = Settings(key=self.secrets[Constants.sendgrid_api_key])
        return EmailClient(settings)

    @api.get("/email_events/<message_id>")
    def email_events(self) -> list[Response | Effect]:
        """Retrieve email events for a specific message.

        Returns:
            list[Response | Effect]: JSON response with email event data or error message.
        """
        message_id = self.request.path_params["message_id"]
        client = self._sendgrid_client()
        try:
            result = [
                JSONResponse(
                    client.logged_email(message_id).to_dict(),
                    status_code=HTTPStatus(HTTPStatus.OK),
                )
            ]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.post("/emails_sent")
    def emails_sent(self) -> list[Response | Effect]:
        """Retrieve a list of sent emails based on search criteria.

        Expects JSON body with optional filters:
            - emailTo: Filter by recipient email address
            - onDay: Filter by date (YYYY-MM-DD format)
            - maxLogs: Maximum number of logs to retrieve

        Returns:
            list[Response | Effect]: JSON response with list of sent emails or error message.
        """
        content = self.request.json()
        to_email = content.get("emailTo")
        on_day = content.get("onDay")
        max_logs = content.get("maxLogs")

        client = self._sendgrid_client()
        try:
            message_created_at = []
            if on_day:
                date_time = datetime.strptime(on_day, "%Y-%m-%d")
                message_created_at = [
                    CriterionDatetime(
                        date_time=date_time,
                        operation=CriterionOperation.GREATER_THAN_OR_EQUAL,
                    ),
                ]
                next_date = date_time + timedelta(days=1)
                if next_date < datetime.now():
                    message_created_at.append(
                        CriterionDatetime(
                            date_time=next_date,
                            operation=CriterionOperation.LOWER_THAN_OR_EQUAL,
                        )
                    )

            criteria = LoggedEmailCriteria(
                message_id="",
                subject="",
                to_email=to_email,
                reason="",
                status=[],
                message_created_at=message_created_at,
            )
            result = [
                JSONResponse(
                    [email.to_dict() for email in client.logged_emails(criteria, max_logs)],
                    status_code=HTTPStatus(HTTPStatus.OK),
                )
            ]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.post("/send_email")
    def send_email(self) -> list[Response | Effect]:
        """Send an email via Sendgrid.

        Expects JSON body with:
            - emailFrom: Sender email address
            - emailTo: Recipient email address
            - emailCc: CC recipient (optional)
            - subject: Email subject line
            - body: Email body text
            - inlineUrl: URL for inline image (optional)
            - attachmentUrl: URL for file attachment (optional)

        Returns:
            list[Response | Effect]: JSON response with success status or error message.
        """
        content = self.request.json()
        email_from = content.get("emailFrom")
        email_to = content.get("emailTo")
        email_cc = content.get("emailCc")
        subject = content.get("subject")
        body = content.get("body")
        inline_url = content.get("inlineUrl")
        attachment_url = content.get("attachmentUrl")

        client = self._sendgrid_client()
        try:
            sender = Address(email=email_from, name="Sender")
            reply_tos = [Address(email=email_from, name="ReplyTo")]
            recipients = [
                Recipient(address=Address(email=email_to, name="RecTo"), type=RecipientType.TO)
            ]
            if email_cc:
                cc = Recipient(address=Address(email=email_cc, name="RecCc"), type=RecipientType.CC)
                recipients.append(cc)
            subject = f"{subject} - {datetime.now(UTC).strftime('%H:%M:%S')}"

            bodies = [BodyContent(type="text/plain", value=body)]
            attachments = []
            if inline_url:
                attached = Attachment.from_url_inline(
                    inline_url, {}, "inline_picture.png", "pictureId"
                )
                attachments.append(attached)
                html_body = BodyContent(
                    type="text/html",
                    value=f"<html><body>{body}<br/>"
                    '<img src="cid:pictureId" width="200px"/><br/>'
                    "Bye!</body></html>",
                )
                bodies.append(html_body)

            if attachment_url:
                attached = Attachment.from_url(attachment_url, {}, "attached_picture.png")
                attachments.append(attached)

            email = Email(
                sender=sender,
                reply_tos=reply_tos,
                recipients=recipients,
                subject=subject,
                bodies=bodies,
                attachments=attachments,
                send_at=Email.now(),
            )

            result = [
                JSONResponse(
                    {"successful": client.simple_send(email)},
                    status_code=HTTPStatus(HTTPStatus.OK),
                )
            ]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    def parser_url(self) -> str:
        """Generate the URL for the inbound email parser webhook.

        Returns:
            str: The full webhook URL for receiving inbound emails.
        """
        host = f"https://{self.environment[Constants.customer_identifier]}.canvasmedical.com"
        return f"{host}{Constants.plugin_api_base_route}/inbound_email"

    @api.post("/inbound_webhook")
    def inbound_webhook_toggle(self) -> list[Response | Effect]:
        """Enable or disable the inbound email webhook.

        Expects JSON body with:
            - enabled: Boolean indicating whether to enable or disable
            - hostname: The hostname for the parse setting (required when enabling)

        Returns:
            list[Response | Effect]: JSON response with enabled status or error message.
        """
        content = self.request.json()
        enabled = content.get("enabled")
        hostname = content.get("hostname")

        client = self._sendgrid_client()
        try:
            result = [JSONResponse({"enabled": enabled}, status_code=HTTPStatus(HTTPStatus.OK))]
            # retrieve if the parser has been already defined
            parser_url = self.parser_url()
            parsers = [
                parser.hostname
                for parser in client.parser_setting_list()
                if parser.url == parser_url
            ]
            if enabled and not parsers:
                setting = ParseSetting(
                    url=self.parser_url(),
                    hostname=hostname,
                    spam_check=True,
                    send_raw=False,
                )
                client.parser_setting_add(setting)
            if not enabled and parsers:
                client.parser_setting_delete(parsers[0])

        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.get("/inbound_webhook")
    def inbound_webhook_get(self) -> list[Response | Effect]:
        """Get the current status of the inbound email webhook.

        Returns:
            list[Response | Effect]: JSON response with enabled status and hostname or error message.
        """
        client = self._sendgrid_client()
        try:
            parser_url = self.parser_url()
            parsers = [
                parser for parser in client.parser_setting_list() if parser.url == parser_url
            ]
            response = {"enabled": bool(parsers), "hostname": ""}
            if parsers:
                response["hostname"] = parsers[0].hostname
            result = [JSONResponse(response, status_code=HTTPStatus(HTTPStatus.OK))]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    def webhook_url(self) -> str:
        """Generate the URL for the outbound email status webhook.

        Returns:
            str: The full webhook URL for receiving outbound email events.
        """
        host = f"https://{self.environment[Constants.customer_identifier]}.canvasmedical.com"
        return f"{host}{Constants.plugin_api_base_route}/outbound_email_status"

    @api.post("/outbound_webhook")
    def outbound_webhook_toggle(self) -> list[Response | Effect]:
        """Enable or disable the outbound email event webhook.

        Expects JSON body with:
            - enabled: Boolean indicating whether to enable or disable

        Returns:
            list[Response | Effect]: JSON response with enabled status or error message.
        """
        content = self.request.json()
        enabled = content.get("enabled")
        client = self._sendgrid_client()
        try:
            result = [JSONResponse({"enabled": enabled}, status_code=HTTPStatus(HTTPStatus.OK))]
            # retrieve if the webhook has been already defined
            webhook_url = self.webhook_url()
            webhook_ids = [
                webhook.id for webhook in client.event_webhook_list() if webhook.url == webhook_url
            ]

            if enabled and not webhook_ids:
                event = EventWebhook(
                    url=webhook_url,
                    enabled=True,
                    group_resubscribe=False,
                    group_unsubscribe=False,
                    delivered=True,
                    spam_report=True,
                    bounce=True,
                    unsubscribe=False,
                    processed=True,
                    open=True,
                    click=True,
                    dropped=True,
                    friendly_name="Canvas Plugin Webhook",
                )
                client.event_webhook_add(event)
            if not enabled and webhook_ids:
                client.event_webhook_delete(webhook_ids[0])

        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.get("/outbound_webhook")
    def outbound_webhook_get(self) -> list[Response | Effect]:
        """Get the current status of the outbound email webhook.

        Returns:
            list[Response | Effect]: JSON response with enabled status or error message.
        """
        client = self._sendgrid_client()
        try:
            webhook_url = self.webhook_url()
            enabled = any(
                webhook.id for webhook in client.event_webhook_list() if webhook.url == webhook_url
            )
            result = [JSONResponse({"enabled": enabled}, status_code=HTTPStatus(HTTPStatus.OK))]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.get("/outbound_email_status")
    def last_outbound_status(self) -> list[Response | Effect]:
        """Retrieve the last cached outbound email status events.

        Returns:
            list[Response | Effect]: JSON response with cached outbound email events.
        """
        return [
            JSONResponse(
                self.cache_retrieve("outbound_email_status"), status_code=HTTPStatus(HTTPStatus.OK)
            )
        ]

    @api.post("/outbound_email_status")
    def outbound_status_save(self) -> list[Response | Effect]:
        """Receive and cache outbound email status events from Sendgrid webhook.

        Expects JSON array of email event objects.

        Returns:
            list[Response | Effect]: Response with 200 status code.
        """
        events = [EmailEvent.from_dict(item) for item in self.request.json()]
        self.cache_save("outbound_email_status", [e.to_dict() for e in events])
        log.info(f"outbound status received:{len(events)}")
        return [Response(status_code=HTTPStatus(HTTPStatus.OK))]

    @api.get("/inbound_email")
    def last_inbound_email(self) -> list[Response | Effect]:
        """Retrieve the last cached inbound email.

        Returns:
            list[Response | Effect]: JSON response with cached inbound email data.
        """
        return [
            JSONResponse(
                self.cache_retrieve("inbound_treatment"),
                status_code=HTTPStatus(HTTPStatus.OK),
            )
        ]

    @api.post("/inbound_email")
    def inbound_email_save(self) -> list[Response | Effect]:
        """Receive and cache inbound email from Sendgrid parser webhook.

        Expects multipart form data with email details and attachments.

        Returns:
            list[Response | Effect]: Response with 200 status code.
        """
        form = self.request.form_data()
        message = {}
        files = []
        for key, value in form.multi_items():
            if (
                hasattr(value, "file")
                and hasattr(value, "filename")
                and hasattr(value, "content_type")
            ):
                files.append((key, value))
            else:
                if hasattr(value, "value"):
                    message[key] = value.value
                elif isinstance(value, str):
                    message[key] = value
                else:
                    message[key] = str(value)

        parsed = ParsedEmail.from_dict(message)
        self.cache_save("inbound_treatment", [parsed.to_dict()])
        log.info(f"inbound email received from {parsed.email_from} to {parsed.email_to}")
        return [Response(status_code=HTTPStatus(HTTPStatus.OK))]

    @classmethod
    def cache_save(cls, key: str, payload: list) -> None:
        """Save data to the plugin cache.

        Args:
            key: The cache key to store the data under.
            payload: The list data to cache.
        """
        get_cache().set(key, payload)

    @classmethod
    def cache_retrieve(cls, key: str) -> list:
        """Retrieve data from the plugin cache.

        Args:
            key: The cache key to retrieve data from.

        Returns:
            list: The cached data or an empty list if not found.
        """
        return get_cache().get(key) or []
