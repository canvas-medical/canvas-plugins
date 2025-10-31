from datetime import datetime
from typing import Any
from uuid import UUID

from canvas_sdk.effects import EffectType, _BaseEffect


class CreateEvent(_BaseEffect):
    """Effect to create a Calendar event."""

    class Meta:
        effect_type = EffectType.CALENDAR__EVENT__CREATE

    calendar_id: str | UUID
    title: str
    starts_at: datetime
    ends_at: datetime
    recurrence: str
    recurrence_ends_at: datetime | None = None
    allowed_note_types: list[str] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The event's values."""
        return {
            "calendar_id": self.calendar_id,
            "title": self.title,
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat(),
            "recurrence": self.recurrence,
            "recurrence_ends_at": self.recurrence_ends_at.isoformat()
            if self.recurrence_ends_at
            else None,
            "allowed_note_types": self.allowed_note_types,
        }


class UpdateEvent(_BaseEffect):
    """Effect to update a Calendar event."""

    class Meta:
        effect_type = EffectType.CALENDAR__EVENT__UPDATE

    event_id: str | UUID
    title: str
    starts_at: datetime
    ends_at: datetime
    recurrence: str
    recurrence_ends_at: datetime | None = None
    allowed_note_types: list[str] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The event's values."""
        return {
            "event_id": self.event_id,
            "title": self.title,
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat(),
            "recurrence": self.recurrence,
            "recurrence_ends_at": self.recurrence_ends_at.isoformat()
            if self.recurrence_ends_at
            else None,
            "allowed_note_types": self.allowed_note_types,
        }


class DeleteEvent(_BaseEffect):
    """Effect to delete a Calendar event."""

    class Meta:
        effect_type = EffectType.CALENDAR__EVENT__DELETE

    event_id: str | UUID

    @property
    def values(self) -> dict[str, Any]:
        """The event's values."""
        return {"event_id": self.event_id}


__exports__ = ("CreateEvent", "UpdateEvent", "DeleteEvent")
