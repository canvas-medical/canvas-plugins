from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.sendgrid.constants.status_email import StatusEmail
from canvas_sdk.clients.sendgrid.structures.email_event import EmailEvent
from canvas_sdk.clients.sendgrid.structures.structure import Structure


@dataclass(frozen=True)
class SentEmailDetailed(Structure):
    """Represents a sent email with its current event history."""

    from_email: str
    message_id: str
    subject: str
    to_email: str
    status: StatusEmail
    events: list[EmailEvent]

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create SentEmailDetailed instance from dictionary."""
        return cls(
            from_email=data["from_email"],
            message_id=data["sg_message_id"],
            subject=data["subject"],
            to_email=data["to_email"],
            status=StatusEmail(data["status"]),
            events=[EmailEvent.from_dict(e) for e in data["events"]],
        )

    def to_dict(self) -> dict:
        """Convert sent email detailed to dictionary format."""
        return {
            "fromEmail": self.from_email,
            "messageId": self.message_id,
            "subject": self.subject,
            "toEmail": self.to_email,
            "status": self.status.value,
            "events": [e.to_dict() for e in self.events],
        }


__exports__ = ()
