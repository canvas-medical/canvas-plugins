import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.effects import EffectType, _BaseEffect


class CalendarType(StrEnum):
    """Calendar type."""

    Clinic = "Clinic"
    Administrative = "Admin"


class Calendar(_BaseEffect):
    """Effect to create a Calendar."""

    id: str | UUID | None = None
    provider: str | UUID
    type: CalendarType
    location: str | UUID | None = None
    description: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The Calendar's values."""
        return {
            "id": self.id,
            "provider": self.provider,
            "type": self.type,
            "location": self.location,
            "description": self.description,
        }

    def create(self) -> Effect:
        """Send a CREATE effect for the calendar."""
        self._validate_before_effect("create")

        return Effect(
            type=EffectType.CALENDAR__CREATE,
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


__exports__ = (
    "Calendar",
    "CalendarType",
)
