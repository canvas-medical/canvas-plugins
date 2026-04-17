import json
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
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


class Event(_BaseEffect):
    """Effect to create a Calendar event."""

    calendar_id: str | UUID | None = None
    event_id: str | UUID | None = None
    title: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
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
            "calendar_id": self.calendar_id,
            "title": self.title,
            "starts_at": self.starts_at.isoformat() if self.starts_at else None,
            "ends_at": self.ends_at.isoformat() if self.ends_at else None,
            "recurrence": get_recurrence_string(
                self.recurrence_frequency, self.recurrence_interval, self.recurrence_days
            ),
            "recurrence_ends_at": self.recurrence_ends_at.isoformat()
            if self.recurrence_ends_at
            else None,
            "allowed_note_types": self.allowed_note_types,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        # calendar_id is required for create
        if method == "create" and not self.calendar_id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    "Field 'calendar_id' is required to create an event.",
                    None,
                )
            )

        if method in ("update", "delete") and not self.event_id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'event_id' is required to {method} an event.",
                    None,
                )
            )

        if method in (
            "create",
            "update",
        ):
            if not self.title:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        f"Field 'title' is required to {method} an event.",
                        None,
                    )
                )

            if not self.starts_at:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        f"Field 'starts_at' is required to {method} an event.",
                        None,
                    )
                )

            if not self.ends_at:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        f"Field 'ends_at' is required to {method} an event.",
                        None,
                    )
                )

        return errors

    def create(self) -> Effect:
        """Send a CREATE effect for the calendar event."""
        self._validate_before_effect("create")

        return Effect(
            type=EffectType.CALENDAR__EVENT__CREATE,
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )

    def update(self) -> Effect:
        """Send an UPDATE effect for the calendar event."""
        self._validate_before_effect("update")

        return Effect(
            type=EffectType.CALENDAR__EVENT__UPDATE,
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )

    def delete(self) -> Effect:
        """Send a DELETE effect for the calendar event."""
        self._validate_before_effect("delete")

        return Effect(
            type=EffectType.CALENDAR__EVENT__DELETE,
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


__exports__ = ("Event", "EventRecurrence", "DaysOfWeek")
