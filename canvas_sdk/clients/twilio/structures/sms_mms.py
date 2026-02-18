from dataclasses import dataclass

from canvas_sdk.clients.twilio.structures import Capabilities
from canvas_sdk.clients.twilio.structures.request_failed import RequestFailed


@dataclass(frozen=True)
class SmsMms:
    """Represents an SMS or MMS message to be sent via Twilio.

    Attributes:
        number_from: The sender's phone number.
        number_from_sid: The Twilio SID of the sender's phone number.
        number_to: The recipient's phone number.
        message: The text content of the message.
        media_url: URL of media to attach (for MMS).
        status_callback_url: URL to receive delivery status updates.
    """

    number_from: str
    number_from_sid: str
    number_to: str
    message: str
    media_url: str
    status_callback_url: str

    def to_dict(self) -> dict:
        """Convert the SmsMms to a dictionary representation.

        Returns:
            Dictionary containing all message data.
        """
        return {
            "number_from": self.number_from,
            "number_from_sid": self.number_from_sid,
            "number_to": self.number_to,
            "message": self.message,
            "media_url": self.media_url,
            "status_callback_url": self.status_callback_url,
        }

    def to_api(self, capabilities: Capabilities) -> dict:
        """Convert the SmsMms to Twilio API request format with capability validation.

        Args:
            capabilities: Phone number capabilities to validate against.

        Returns:
            Dictionary formatted for Twilio API request.

        Raises:
            RequestFailed: If the phone number lacks required capabilities or no content is provided.
        """
        result = {
            "To": self.number_to,
            "From": self.number_from,
        }
        if self.media_url:
            if not capabilities.mms:
                raise RequestFailed(0, f"{self.number_from} cannot sent MMS")
            result["MediaUrl"] = self.media_url
        if self.message:
            if not capabilities.sms:
                raise RequestFailed(0, f"{self.number_from} cannot sent SMS")
            result["Body"] = self.message
        if self.status_callback_url:
            result["StatusCallback"] = self.status_callback_url
        if not ("Body" in result or "MediaUrl" in result):
            raise RequestFailed(0, "no content to be sent")
        return result


__exports__ = ()
