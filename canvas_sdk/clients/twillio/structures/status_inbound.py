from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.twillio.constants.message_status import MessageStatus
from canvas_sdk.clients.twillio.structures.helper import Helper


@dataclass(frozen=True)
class StatusInbound:
    """Represents the status callback data for an inbound message from Twilio.

    see https://www.twilio.com/docs/messaging/guides/webhook-request
    """

    account_sid: str
    message_sid: str
    messaging_service_sid: str
    sms_message_sid: str
    sms_sid: str
    sms_status: MessageStatus
    to_country: str
    to_zip: str
    to_state: str
    to_city: str
    from_country: str
    from_zip: str
    from_state: str
    from_city: str
    number_to: str
    number_from: str
    body: str
    count_media: int
    count_segments: int
    media_content_type: list[str]
    media_url: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a StatusInbound instance from a dictionary.

        Args:
            data: Dictionary containing the inbound status data from Twilio.

        Returns:
            StatusInbound instance populated with the provided data.
        """
        media_content_type: list[str] = []
        media_url: list[str] = []
        for idx in range(int(data["NumMedia"])):
            key_type = f"MediaContentType{idx}"
            key_url = f"MediaUrl{idx}"
            if not (key_type in data and key_url in data):
                break
            media_content_type.append(data[key_type])
            media_url.append(data[key_url])

        return cls(
            account_sid=data["AccountSid"],
            message_sid=data["MessageSid"],
            messaging_service_sid=data["MessagingServiceSid"],
            sms_message_sid=data["SmsMessageSid"],
            sms_sid=data["SmsSid"],
            sms_status=MessageStatus(data["SmsStatus"]),
            to_country=data["ToCountry"],
            to_zip=data["ToZip"],
            to_state=data["ToState"],
            to_city=data["ToCity"],
            from_country=data["FromCountry"],
            from_zip=data["FromZip"],
            from_state=data["FromState"],
            from_city=data["FromCity"],
            number_to=data["To"],
            number_from=data["From"],
            body=data["Body"],
            count_media=int(data["NumMedia"]),
            count_segments=int(data["NumSegments"]),
            media_content_type=media_content_type,
            media_url=media_url,
        )

    @classmethod
    def callback_inbound(cls, raw_body: str) -> Self:
        """Parse a Twilio inbound message callback body.

        Args:
            raw_body: The raw URL-encoded callback body from Twilio.

        Returns:
            StatusInbound instance with parsed callback data.
        """
        return cls.from_dict(Helper.parse_body(raw_body))


__exports__ = ()
