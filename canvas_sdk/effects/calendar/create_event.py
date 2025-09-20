from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from canvas_sdk.effects import EffectType, _BaseEffect


class EventRecurrence(StrEnum):
    """Calendar event recurrence."""

    Daily = "FREQ=DAILY"
    Weekly = "FREQ=WEEKLY"


class CreateEvent(_BaseEffect):
    """Effect to create a Calendar event."""

    class Meta:
        effect_type = EffectType.CALENDAR__EVENT__CREATE

    calendar_id: str | UUID
    title: str
    starts_at: datetime
    ends_at: datetime
    recurrence: EventRecurrence

    @property
    def values(self) -> dict[str, Any]:
        """The event's values."""
        return {
            "calendar_id": self.calendar_id,
            "title": self.title,
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat(),
            "recurrence": self.recurrence,
        }


__exports__ = (
    "CreateEvent",
    "EventRecurrence",
)
