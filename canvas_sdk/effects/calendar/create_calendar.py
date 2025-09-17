from enum import StrEnum
from typing import Any
from uuid import UUID

from canvas_sdk.effects import EffectType, _BaseEffect


class CalendarType(StrEnum):
    """Calendar type."""

    Clinic = "Clinic"
    Administrative = "Admin"


class CreateCalendar(_BaseEffect):
    """Effect to create a Calendar."""

    class Meta:
        effect_type = EffectType.CALENDAR__CREATE

    id: str | UUID | None = None
    provider: str | UUID
    type: CalendarType
    description: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The Calendar's values."""
        return {
            "id": self.id,
            "provider": self.provider,
            "type": self.type,
            "description": self.description,
        }


__exports__ = (
    "CreateCalendar",
    "CalendarType",
)
