from dataclasses import dataclass
from datetime import datetime
from typing import Self

from canvas_sdk.clients.sendgrid.constants.event_email import EventEmail


@dataclass(frozen=True)
class EmailEvent:
    """Represents a single event in an email's lifecycle."""

    event: EventEmail
    email: str
    message_id: str
    event_id: str
    on_datetime: datetime
    # depending on the event
    reason: str
    response: str
    url: str
    attempt: int

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create EmailEvent instance from dictionary."""
        event = EventEmail(data["event"])
        if event == EventEmail.RECEIVED:
            email = ""
            message_id = data["recv_msgid"]
        else:
            email = data["email"]
            message_id = data["sg_message_id"]

        return cls(
            event=event,
            email=email,
            message_id=message_id,
            event_id=data["sg_event_id"],
            on_datetime=datetime.fromtimestamp(data["timestamp"]),
            # depending on the event
            reason=data.get("reason") or "",  # bounce, dropped
            response=data.get("response") or "",  # delivered
            url=data.get("url") or "",  # click, open
            attempt=data.get("attempt") or -1,  # deferred
        )

    def to_dict(self) -> dict:
        """Convert email event to dictionary format."""
        return {
            "event": self.event.value,
            "email": self.email,
            "messageId": self.message_id,
            "eventId": self.event_id,
            "datetime": self.on_datetime.isoformat(),
            "reason": self.reason,
            "response": self.response,
            "url": self.url,
            "attempt": self.attempt,
        }


__exports__ = ()
