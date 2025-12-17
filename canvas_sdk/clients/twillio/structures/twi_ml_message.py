from dataclasses import dataclass
from typing import Self
from xml.etree.ElementTree import Element, SubElement, tostring

from canvas_sdk.clients.twillio.constants.constants import Constants
from canvas_sdk.clients.twillio.constants.http_method import HttpMethod


@dataclass(frozen=True)
class TwiMlMessage:
    """Represents a TwiML message for sending SMS via Twilio with optional media attachments."""

    number_to: str
    number_from: str
    status_callback_url: str
    message_text: str
    media_url: str
    method: HttpMethod | None

    @classmethod
    def instance(cls, message_text: str) -> Self:
        """Create a TwiMlMessage instance with only message text.

        Args:
            message_text: The text content of the message.

        Returns:
            TwiMlMessage instance with empty recipient, sender, and callback fields.
        """
        return cls(
            number_to="",
            number_from="",
            status_callback_url="",
            message_text=message_text,
            media_url="",
            method=None,
        )

    @classmethod
    def instance_with_media(cls, message_text: str, media_url: str) -> Self:
        """Create a TwiMlMessage instance with message text and media attachment.

        Args:
            message_text: The text content of the message.
            media_url: URL of the media file to attach.

        Returns:
            TwiMlMessage instance with media URL and empty recipient, sender, and callback fields.
        """
        return cls(
            number_to="",
            number_from="",
            status_callback_url="",
            message_text=message_text,
            media_url=media_url,
            method=None,
        )

    def to_xml(self) -> str:
        """Generate TwiML XML for sending an SMS message.

        Returns:
            XML string formatted as TwiML with message content and optional media.
        """
        response = Element("Response")
        message = SubElement(response, "Message", self._build_attributes())

        if self.media_url:
            # when media is present, Body must be a separate element
            body = SubElement(message, "Body")
            body.text = self.message_text[: Constants.sms_max_length]

            media = SubElement(message, "Media")
            media.text = self.media_url
        else:
            # when no media, text goes directly in Message element
            message.text = self.message_text[: Constants.sms_max_length]

        xml_str = tostring(response, encoding="unicode", method="xml")
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

    def _build_attributes(self) -> dict[str, str]:
        """Build the Message element attributes.

        Returns:
            Dictionary of non-empty attributes for the TwiML Message element.
        """
        return {
            k: v
            for k, v in [
                ("to", self.number_to),
                ("from", self.number_from),
                ("statusCallback", self.status_callback_url),
                ("method", self.method.value if self.method else None),
            ]
            if v
        }


__exports__ = ()
