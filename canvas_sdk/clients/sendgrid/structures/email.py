from dataclasses import dataclass
from datetime import UTC, datetime

from canvas_sdk.clients.sendgrid.structures.address import Address
from canvas_sdk.clients.sendgrid.structures.attachment import Attachment
from canvas_sdk.clients.sendgrid.structures.body_content import BodyContent
from canvas_sdk.clients.sendgrid.structures.recipient import Recipient


@dataclass(frozen=True)
class Email:
    """Represents a complete email message with all components."""

    sender: Address
    reply_tos: list[Address]
    recipients: list[Recipient]
    subject: str
    bodies: list[BodyContent]
    attachments: list[Attachment]
    send_at: int

    @classmethod
    def now(cls) -> int:
        """Get current timestamp for immediate sending."""
        return cls.timestamp(datetime.now(tz=UTC))

    @classmethod
    def timestamp(cls, now: datetime) -> int:
        """Convert datetime to Unix timestamp."""
        return int(now.timestamp())


__exports__ = ()
