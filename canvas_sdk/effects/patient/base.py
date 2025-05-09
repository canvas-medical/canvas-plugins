import datetime
import json
from dataclasses import dataclass
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.v1.data import PracticeLocation, Staff
from canvas_sdk.v1.data.common import ContactPointSystem, ContactPointUse, PersonSex


@dataclass
class PatientContactPoint:
    """A class representing a patient contact point."""

    system: ContactPointSystem
    value: str
    use: ContactPointUse
    rank: int
    has_consent: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the contact point to a dictionary."""
        return {
            "system": self.system.value,
            "value": self.value,
            "use": self.use.value,
            "rank": self.rank,
            "has_consent": self.has_consent,
        }


class Patient(TrackableFieldsModel):
    """Effect to create a Patient record."""

    class Meta:
        effect_type = "PATIENT"

    first_name: str
    last_name: str
    middle_name: str | None = None
    birthdate: datetime.date | None = None
    prefix: str | None = None
    suffix: str | None = None
    sex_at_birth: PersonSex | None = None
    nickname: str | None = None
    social_security_number: str | None = None
    administrative_note: str | None = None
    clinical_note: str | None = None
    default_location_id: str | None = None
    default_provider_id: str | None = None
    previous_names: list[str] | None = None
    contact_points: list[PatientContactPoint] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the patient as a dictionary."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "previous_names": self.previous_names or [],
            "birthdate": self.birthdate.isoformat() if self.birthdate else None,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "sex_at_birth": self.sex_at_birth.value if self.sex_at_birth else None,
            "nickname": self.nickname,
            "social_security_number": self.social_security_number,
            "administrative_note": self.administrative_note,
            "clinical_note": self.clinical_note,
            "default_location": self.default_location_id,
            "default_provider": self.default_provider_id,
            "contact_points": [cp.to_dict() for cp in self.contact_points]
            if self.contact_points
            else None,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if (
            self.default_location_id
            and not PracticeLocation.objects.filter(id=self.default_location_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Practice location with ID {self.default_location_id} does not exist.",
                    self.default_location_id,
                )
            )

        if (
            self.default_provider_id
            and not Staff.objects.filter(id=self.default_provider_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Provider with ID {self.default_provider_id} does not exist.",
                    self.default_provider_id,
                )
            )

        return errors

    def create(self) -> Effect:
        """Create a new Patient."""
        self._validate_before_effect("create")

        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


__exports__ = ("Patient", "PatientContactPoint")
