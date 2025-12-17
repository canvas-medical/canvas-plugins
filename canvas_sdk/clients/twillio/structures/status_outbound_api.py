from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.twillio.constants.message_status import MessageStatus
from canvas_sdk.clients.twillio.structures.helper import Helper


@dataclass(frozen=True)
class StatusOutboundApi:
    """Represents the status callback data for an outbound API message from Twilio.

    see https://www.twilio.com/docs/messaging/guides/outbound-message-status-in-status-callbacks
    """

    account_sid: str
    message_sid: str
    sms_sid: str
    sms_status: MessageStatus
    message_status: MessageStatus
    number_to: str
    number_from: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a StatusOutboundApi instance from a dictionary.

        Args:
            data: Dictionary containing the outbound API status data from Twilio.

        Returns:
            StatusOutboundApi instance populated with the provided data.
        """
        return cls(
            account_sid=data["AccountSid"],
            message_sid=data["MessageSid"],
            sms_sid=data["SmsSid"],
            sms_status=MessageStatus(data["SmsStatus"]),
            message_status=MessageStatus(data["MessageStatus"]),
            number_to=data["To"],
            number_from=data["From"],
        )

    @classmethod
    def callback_outbound_api(cls, raw_body: str) -> Self:
        """Parse a Twilio outbound API status callback body.

        Args:
            raw_body: The raw URL-encoded callback body from Twilio.

        Returns:
            StatusOutboundApi instance with parsed callback data.
        """
        return cls.from_dict(Helper.parse_body(raw_body))


__exports__ = ()
