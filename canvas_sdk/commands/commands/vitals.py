from enum import Enum
from typing import Optional

from pydantic import conint, constr

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class VitalsCommand(BaseCommand):
    """A class for managing a Vitals command within a specific note."""

    class Meta:
        key = "vitals"
        commit_required_fields = ()

    class BodyTemperatureSite(Enum):
        AXILLARY = 0
        ORAL = 1
        RECTAL = 2
        TEMPORAL = 3
        TYMPANIC = 4

    class BloodPressureSite(Enum):
        SITTING_RIGHT_UPPER = 0
        SITTING_LEFT_UPPER = 1
        SITTING_RIGHT_LOWER = 2
        SITTING_LEFT_LOWER = 3
        STANDING_RIGHT_UPPER = 4
        STANDING_LEFT_UPPER = 5
        STANDING_RIGHT_LOWER = 6
        STANDING_LEFT_LOWER = 7
        SUPINE_RIGHT_UPPER = 8
        SUPINE_LEFT_UPPER = 9
        SUPINE_RIGHT_LOWER = 10
        SUPINE_LEFT_LOWER = 11

    class PulseRhythm(Enum):
        REGULAR = 0
        IRREGULARLY_IRREGULAR = 1
        REGULARLY_IRREGULAR = 2

    height: conint(ge=10, le=108) | None = None  # type: ignore[valid-type]
    weight_lbs: conint(ge=1, le=1500) | None = None  # type: ignore[valid-type]
    weight_oz: int | None = None
    waist_circumference: conint(ge=20, le=200) | None = None  # type: ignore[valid-type]
    body_temperature: conint(ge=85, le=107) | None = None  # type: ignore[valid-type]
    body_temperature_site: BodyTemperatureSite | None = None
    blood_pressure_systole: conint(ge=30, le=305) | None = None  # type: ignore[valid-type]
    blood_pressure_diastole: conint(ge=20, le=180) | None = None  # type: ignore[valid-type]
    blood_pressure_position_and_site: BloodPressureSite | None = None
    pulse: conint(ge=30, le=250) | None = None  # type: ignore[valid-type]
    pulse_rhythm: PulseRhythm | None = None
    respiration_rate: conint(ge=6, le=60) | None = None  # type: ignore[valid-type]
    oxygen_saturation: conint(ge=60, le=100) | None = None  # type: ignore[valid-type]
    note: constr(max_length=150) | None = None  # type: ignore[valid-type]

    @property
    def values(self) -> dict:
        """The Vitals command's field values."""
        return {
            "height": self.height,
            "weight_lbs": self.weight_lbs,
            "weight_oz": self.weight_oz,
            "waist_circumference": self.waist_circumference,
            "body_temperature": self.body_temperature,
            "body_temperature_site": (
                self.body_temperature_site.value if self.body_temperature_site else None
            ),
            "blood_pressure_systole": self.blood_pressure_systole,
            "blood_pressure_diastole": self.blood_pressure_diastole,
            "blood_pressure_position_and_site": (
                self.blood_pressure_position_and_site.value
                if self.blood_pressure_position_and_site
                else None
            ),
            "pulse": self.pulse,
            "pulse_rhythm": self.pulse_rhythm.value if self.pulse_rhythm else None,
            "respiration_rate": self.respiration_rate,
            "oxygen_saturation": self.oxygen_saturation,
            "note": self.note,
        }
