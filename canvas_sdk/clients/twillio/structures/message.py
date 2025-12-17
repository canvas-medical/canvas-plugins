from dataclasses import dataclass
from datetime import datetime
from typing import Self

from canvas_sdk.clients.twillio.constants.constants import Constants
from canvas_sdk.clients.twillio.constants.message_direction import MessageDirection
from canvas_sdk.clients.twillio.constants.message_status import MessageStatus
from canvas_sdk.clients.twillio.structures.helper import Helper
from canvas_sdk.clients.twillio.structures.structure import Structure


@dataclass(frozen=True)
class Message(Structure):
    """Represents a Twilio message with all its associated metadata and status information."""

    sid: str
    body: str
    date_created: datetime
    date_sent: datetime | None
    date_updated: datetime
    direction: MessageDirection
    number_from: str
    number_to: str
    price: str | None  # float
    price_unit: str
    error_code: int | None
    error_message: str | None
    uri: str
    count_media: int | None
    count_segments: int
    status: MessageStatus
    sub_resource_uris: dict[str, str] | None

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a Message instance from a dictionary.

        Args:
            data: Dictionary containing the message data from Twilio API.

        Returns:
            Message instance populated with the provided data.
        """
        return cls(
            sid=data["sid"],
            body=data["body"],
            date_created=Helper.to_datetime(data, "date_created"),
            date_sent=Helper.to_datetime_or_none(data, "date_sent"),
            date_updated=Helper.to_datetime(data, "date_updated"),
            direction=MessageDirection(data["direction"]),
            number_from=data["from"],
            number_to=data["to"],
            price=data.get("price"),
            price_unit=data["price_unit"],
            error_code=data.get("error_code"),
            error_message=data.get("error_message"),
            uri=data["uri"],
            count_media=data["num_media"],
            count_segments=data["num_segments"],
            status=MessageStatus(data["status"]),
            sub_resource_uris=data["subresource_uris"],
        )

    def to_dict(self) -> dict:
        """Convert the Message to a dictionary representation.

        Returns:
            Dictionary containing all message data in both Twilio and standard formats.
        """
        return {
            "sid": self.sid,
            "body": self.body,
            "date_created": Helper.from_datetime(self.date_created, Constants.twilio_date),
            "date_sent": Helper.from_datetime_or_none(self.date_sent, Constants.twilio_date),
            "date_updated": Helper.from_datetime(self.date_updated, Constants.twilio_date),
            "created": Helper.from_datetime(self.date_created, Constants.standard_date),
            "sent": Helper.from_datetime_or_none(self.date_sent, Constants.standard_date),
            "updated": Helper.from_datetime(self.date_updated, Constants.standard_date),
            "direction": self.direction.value,
            "from": self.number_from,
            "to": self.number_to,
            "price": self.price,
            "price_unit": self.price_unit,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "uri": self.uri,
            "num_media": self.count_media,
            "num_segments": self.count_segments,
            "status": self.status.value,
            "subresource_uris": self.sub_resource_uris,
        }


__exports__ = ()
