from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Self

from canvas_sdk.clients.sendgrid.constants import Constants
from canvas_sdk.clients.sendgrid.structures.event_webhook import EventWebhook


@dataclass(frozen=True)
class EventWebhookRecord(EventWebhook):
    """Represents a stored event webhook with ID and timestamps."""

    id: str
    public_key: str
    created_date: datetime
    updated_date: datetime

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create EventWebhookRecord instance from dictionary."""
        parent = EventWebhook.from_dict(data)
        return cls(
            **asdict(parent),
            id=data["id"],
            public_key=data.get("public_key") or "",
            created_date=datetime.fromisoformat(data["created_date"]),
            updated_date=datetime.fromisoformat(data["updated_date"]),
        )

    def to_dict(self) -> dict:
        """Convert event webhook record to dictionary format."""
        return super().to_dict() | {
            "id": self.id,
            "public_key": self.public_key,
            "created_date": self.created_date.strftime(Constants.rfc3339_format),
            "updated_date": self.created_date.strftime(Constants.rfc3339_format),
        }


__exports__ = ()
