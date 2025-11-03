from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from canvas_sdk.effects import EffectType, _BaseEffect


class EventRecurrence(StrEnum):
    """Calendar event recurrence."""

    Daily = "DAILY"
    Weekly = "WEEKLY"


class DaysOfWeek(StrEnum):
    """Days of the week."""

    Monday = "MO"
    Tuesday = "TU"
    Wednesday = "WE"
    Thursday = "TH"
    Friday = "FR"
    Saturday = "SA"
    Sunday = "SU"


def get_recurrence_string(
    frequency: EventRecurrence | None, interval: int | None, days_of_week: list[DaysOfWeek] | None
) -> str:
    """Generate the recurrence string for an event."""
    parts = [
        f"FREQ={frequency}" if frequency else "",
        f"INTERVAL={interval}" if interval else "",
        f"BYDAY={','.join(list(map(str, days_of_week)))}" if days_of_week else "",
    ]

    return ";".join(filter(bool, parts))


class CreateEvent(_BaseEffect):
    """Effect to create a Calendar event."""

    class Meta:
        effect_type = EffectType.CALENDAR__EVENT__CREATE

    calendar_id: str | UUID
    title: str
    starts_at: datetime
    ends_at: datetime
    recurrence_frequency: EventRecurrence | None = None
    recurrence_interval: int | None = None
    recurrence_days: list[DaysOfWeek] | None = None
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
            "recurrence": get_recurrence_string(
                self.recurrence_frequency, self.recurrence_interval, self.recurrence_days
            ),
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
    recurrence_frequency: EventRecurrence | None = None
    recurrence_interval: int | None = None
    recurrence_days: list[DaysOfWeek] | None = None
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
            "recurrence": get_recurrence_string(
                self.recurrence_frequency, self.recurrence_interval, self.recurrence_days
            ),
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


__exports__ = ("CreateEvent", "UpdateEvent", "DeleteEvent", "EventRecurrence", "DaysOfWeek")
