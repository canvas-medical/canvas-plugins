import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import NonNegativeInt

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.effects import EffectType, _BaseEffect
from canvas_sdk.effects.base import validate_delay_seconds


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

    @validate_delay_seconds
    def create(self, delay_seconds: NonNegativeInt | None = None) -> Effect:
        """Send a CREATE effect for the calendar."""
        self._validate_before_effect("create")

        effect = Effect(
            type=EffectType.CALENDAR__CREATE,
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )
        if delay_seconds is not None:
            effect.delay_seconds = delay_seconds
        return effect


__exports__ = (
    "Calendar",
    "CalendarType",
)
