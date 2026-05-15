from dataclasses import dataclass
from datetime import datetime
from typing import Self

from canvas_sdk.clients.sendgrid.constants.status_email import StatusEmail
from canvas_sdk.clients.sendgrid.structures.structure import Structure


@dataclass(frozen=True)
class SentEmail(Structure):
    """Represents a sent email with basic information."""

    from_email: str
    message_id: str
    subject: str
    to_email: str
    reason: str
    status: StatusEmail
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create SentEmail instance from dictionary."""
        return cls(
            from_email=data["from_email"],
            message_id=data["sg_message_id"],
            subject=data["subject"],
            to_email=data["to_email"],
            reason=data["reason"],
            status=StatusEmail(data["status"]),
            created_at=datetime.fromisoformat(data["sg_message_id_created_at"]),
        )

    def to_dict(self) -> dict:
        """Convert sent email detailed to dictionary format."""
        return {
            "from_email": self.from_email,
            "message_id": self.message_id,
            "subject": self.subject,
            "to_email": self.to_email,
            "reason": self.reason,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }


__exports__ = ()
