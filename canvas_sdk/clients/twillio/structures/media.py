from dataclasses import dataclass
from datetime import datetime
from typing import Self

from canvas_sdk.clients.twillio.constants.constants import Constants
from canvas_sdk.clients.twillio.structures.helper import Helper
from canvas_sdk.clients.twillio.structures.structure import Structure


@dataclass(frozen=True)
class Media(Structure):
    """Represents media attached to a Twilio message.

    Attributes:
        sid: The unique identifier for the media resource.
        content_type: MIME type of the media (e.g., 'image/jpeg').
        date_created: When the media was created.
        date_updated: When the media was last updated.
        parent_sid: The message SID this media belongs to.
        uri: The URI path to access this media resource.
    """

    sid: str
    content_type: str
    date_created: datetime
    date_updated: datetime
    parent_sid: str
    uri: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a Media instance from a dictionary.

        Args:
            data: Dictionary containing media data from Twilio API.

        Returns:
            Media instance populated with the provided data.
        """
        return cls(
            sid=data["sid"],
            content_type=data["content_type"],
            date_created=Helper.to_datetime(data, "date_created"),
            date_updated=Helper.to_datetime(data, "date_updated"),
            parent_sid=data["parent_sid"],
            uri=data["uri"],
        )

    def to_dict(self) -> dict:
        """Convert the Media to a dictionary representation.

        Returns:
            Dictionary containing all media data in both Twilio and standard formats.
        """
        return {
            "sid": self.sid,
            "content_type": self.content_type,
            "date_created": Helper.from_datetime(self.date_created, Constants.twilio_date),
            "date_updated": Helper.from_datetime(self.date_updated, Constants.twilio_date),
            "created": Helper.from_datetime(self.date_created, Constants.standard_date),
            "updated": Helper.from_datetime(self.date_updated, Constants.standard_date),
            "parent_sid": self.parent_sid,
            "uri": self.uri,
        }


__exports__ = ()
