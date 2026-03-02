import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.utils import Http


class PatientSync(BaseHandler):
    """Syncs patient updates to an external webhook and notifies Slack on failure."""

    RESPONDS_TO = EventType.Name(EventType.PATIENT_UPDATED)

    @property
    def webhook_url(self) -> str:
        """Return the webhook URL for posting patient updates."""
        return self.secrets.get("PARTNER_WEBHOOK_URL", "")

    @property
    def webhook_api_key(self) -> str:
        """Return the API key for webhook requests."""
        return self.secrets.get("PARTNER_API_KEY", "")

    @property
    def webhook_headers(self) -> dict[str, str]:
        """Return the request headers for webhook requests."""
        return {"X-API-Key": self.webhook_api_key, "Content-Type": "application/json"}

    @property
    def slack_url(self) -> str:
        """Return the Slack endpoint URL for error notifications."""
        return self.secrets.get("SLACK_ENDPOINT_URL", "")

    @property
    def slack_api_key(self) -> str:
        """Return the API key for Slack requests."""
        return self.secrets.get("SLACK_API_KEY", "")

    @property
    def slack_headers(self) -> dict[str, str]:
        """Return the request headers for Slack API requests."""
        return {"Authorization": f"Bearer {self.slack_api_key}", "Content-Type": "application/json"}

    def _send_slack_notification(
        self,
        http: Http,
        canvas_patient_id: str,
        error_details: str,
        status_code: int | None = None,
    ) -> None:
        """Send an error notification to Slack.

        Args:
            http: The Http client to use for posting.
            canvas_patient_id: The Canvas patient ID that failed to sync.
            error_details: The error message or response text.
            status_code: Optional HTTP status code from webhook response.
        """
        # If no Slack URL or API key configured, skip sending notification
        if not self.slack_url or not self.slack_api_key:
            return

        text_parts = [
            "*Patient Update Sync Failed*\n",
            f"*Patient ID:* {canvas_patient_id}",
        ]

        if status_code is not None:
            text_parts.append(f"*Webhook Status:* {status_code}")

        text_parts.append(f"*Error:* {error_details[:500]}")

        error_message = {
            "text": f"Patient update webhook failed for patient {canvas_patient_id}",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": "\n".join(text_parts)}}
            ],
        }

        http.post(
            self.slack_url,
            json=error_message,
            headers=self.slack_headers,
        )

    def compute(self) -> list[Effect]:
        """Post patient update to webhook and notify Slack on failure."""
        # If no webhook URL or API key configured, skip processing
        if not self.webhook_url or not self.webhook_api_key:
            return []

        canvas_patient_id = self.target
        http = Http()

        # Prepare the payload to send to the webhook
        webhook_payload = {
            "canvas_patient_id": canvas_patient_id,
        }

        # Post to the webhook
        try:
            webhook_response = http.post(
                self.webhook_url,
                json=webhook_payload,
                headers=self.webhook_headers,
            )
        except Exception as e:
            # Connection error, send error notification to Slack
            self._send_slack_notification(http, canvas_patient_id, str(e))

            # Log the error
            log_payload = {
                "event": "webhook_connection_error",
                "patient_id": canvas_patient_id,
                "error": str(e),
            }
            return [Effect(type=EffectType.LOG, payload=json.dumps(log_payload))]

        # Check if the webhook response was successful (200-299 status codes)
        if webhook_response.status_code < 200 or webhook_response.status_code >= 300:
            # Non-200 response, send error notification to Slack
            self._send_slack_notification(
                http,
                canvas_patient_id,
                webhook_response.text,
                status_code=webhook_response.status_code,
            )

            # Log the error
            log_payload = {
                "event": "webhook_failure",
                "patient_id": canvas_patient_id,
                "status_code": webhook_response.status_code,
                "error": webhook_response.text,
            }
            return [Effect(type=EffectType.LOG, payload=json.dumps(log_payload))]

        # Success - log the successful sync
        log_payload = {
            "event": "webhook_success",
            "patient_id": canvas_patient_id,
            "status_code": webhook_response.status_code,
        }
        return [Effect(type=EffectType.LOG, payload=json.dumps(log_payload))]
