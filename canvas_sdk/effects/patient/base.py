import datetime
import json
from dataclasses import dataclass
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects.metadata import Metadata as PatientMetadata
from canvas_sdk.v1.data import Patient as PatientModel
from canvas_sdk.v1.data import PracticeLocation, Staff
from canvas_sdk.v1.data.common import (
    AddressType,
    AddressUse,
    ContactPointSystem,
    ContactPointUse,
    PersonSex,
)


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


@dataclass
class PatientExternalIdentifier:
    """A class representing a patient external identifier."""

    value: str
    system: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the external identifier to a dictionary."""
        return {
            "system": self.system,
            "value": self.value,
        }


@dataclass
class PatientPreferredPharmacy:
    """A class representing a preferred pharmacy."""

    ncpdp_id: str
    default: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert the preferred pharmacy to a dictionary."""
        return {
            "ncpdp_id": self.ncpdp_id,
            "default": self.default,
        }


@dataclass
class PatientAddress:
    """A class representing a patient address."""

    line1: str
    country: str
    line2: str | None = None
    use: AddressUse = AddressUse.HOME
    type: AddressType = AddressType.BOTH
    city: str | None = None
    district: str | None = None
    state_code: str | None = None
    postal_code: str | None = None
    longitude: float | None = None
    latitude: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the address to a dictionary."""
        return {
            "line1": self.line1,
            "line2": self.line2,
            "country": self.country,
            "use": self.use.value,
            "type": self.type.value,
            "city": self.city,
            "district": self.district,
            "state_code": self.state_code,
            "postal_code": self.postal_code,
            "longitude": self.longitude,
            "latitude": self.latitude,
        }


class Patient(TrackableFieldsModel):
    """Effect to create a Patient record."""

    class Meta:
        effect_type = "PATIENT"

    patient_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
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
    external_identifiers: list[PatientExternalIdentifier] | None = None
    preferred_pharmacies: list[PatientPreferredPharmacy] | None = None
    addresses: list[PatientAddress] | None = None
    metadata: list[PatientMetadata] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the patient as a dictionary."""
        values = super().values

        if self.is_dirty("contact_points"):
            values["contact_points"] = (
                [cp.to_dict() for cp in self.contact_points]
                if self.contact_points is not None
                else None
            )

        if self.is_dirty("external_identifiers"):
            values["external_identifiers"] = (
                [ids.to_dict() for ids in self.external_identifiers]
                if self.external_identifiers is not None
                else None
            )

        if self.is_dirty("addresses"):
            values["addresses"] = (
                [addr.to_dict() for addr in self.addresses] if self.addresses is not None else None
            )

        if self.is_dirty("preferred_pharmacies"):
            values["preferred_pharmacies"] = (
                [pharmacy.to_dict() for pharmacy in self.preferred_pharmacies]
                if self.preferred_pharmacies
                else None
            )

        if self.is_dirty("metadata"):
            values["metadata"] = (
                [md.to_dict() for md in self.metadata] if self.metadata is not None else None
            )

        return values

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        # Validate create-specific requirements
        if method == "create":
            if self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Patient ID should not be set when creating a new patient.",
                        self.patient_id,
                    )
                )

            # first_name and last_name are required for create
            if not self.first_name:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "First name is required when creating a new patient.",
                        self.first_name,
                    )
                )

            if not self.last_name:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Last name is required when creating a new patient.",
                        self.last_name,
                    )
                )

        # Validate update-specific requirements
        if method == "update":
            if not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Patient ID must be set when updating an existing patient.",
                        self.patient_id,
                    )
                )
            elif not PatientModel.objects.filter(id=self.patient_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Patient with ID {self.patient_id} does not exist.",
                        self.patient_id,
                    )
                )

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

    def update(self) -> Effect:
        """Update an existing Patient."""
        self._validate_before_effect("update")

        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


__exports__ = (
    "Patient",
    "PatientAddress",
    "PatientContactPoint",
    "PatientExternalIdentifier",
    "PatientMetadata",
    "PatientPreferredPharmacy",
)
