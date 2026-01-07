import datetime
import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.v1.data.observation import Observation as ObservationModel


@dataclass
class CodingData:
    """A class representing coding data for observations, components, and values."""

    code: str
    display: str
    system: str
    version: str = ""
    user_selected: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert the coding to a dictionary."""
        return {
            "code": self.code,
            "display": self.display,
            "system": self.system,
            "version": self.version,
            "user_selected": self.user_selected,
        }


@dataclass
class ObservationComponentData:
    """A class representing observation component data."""

    value_quantity: str
    value_quantity_unit: str
    name: str
    codings: list[CodingData] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the component to a dictionary."""
        return {
            "value_quantity": self.value_quantity,
            "value_quantity_unit": self.value_quantity_unit,
            "name": self.name,
            "codings": ([c.to_dict() for c in self.codings] if self.codings is not None else None),
        }


class Observation(TrackableFieldsModel):
    """Effect to create or update an Observation record."""

    class Meta:
        effect_type = "OBSERVATION"

    observation_id: str | UUID | None = None  # For updates
    patient_id: str | None = None
    is_member_of_id: str | UUID | None = None  # Reference to parent Observation
    category: str | list[str] | None = None
    units: str | None = None
    value: str | None = None
    note_id: int | None = None
    name: str | None = None
    effective_datetime: datetime.datetime | None = None

    # Nested related objects
    codings: list[CodingData] | None = None
    components: list[ObservationComponentData] | None = None
    value_codings: list[CodingData] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the observation as a dictionary."""
        values = super().values

        # Handle nested object serialization
        if self.is_dirty("codings"):
            values["codings"] = (
                [c.to_dict() for c in self.codings] if self.codings is not None else None
            )

        if self.is_dirty("components"):
            values["components"] = (
                [comp.to_dict() for comp in self.components]
                if self.components is not None
                else None
            )

        if self.is_dirty("value_codings"):
            values["value_codings"] = (
                [vc.to_dict() for vc in self.value_codings]
                if self.value_codings is not None
                else None
            )

        return values

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the observation data."""
        errors = super()._get_error_details(method)

        # Validate create-specific requirements
        if method == "create":
            if self.observation_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Observation ID should not be set when creating a new observation.",
                        self.observation_id,
                    )
                )
            if not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Patient ID is required when creating a new observation.",
                        self.patient_id,
                    )
                )
            if not self.name:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Name is required when creating a new observation.",
                        self.name,
                    )
                )
            if not self.effective_datetime:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Effective datetime is required when creating a new observation.",
                        self.effective_datetime,
                    )
                )

        # Validate update-specific requirements
        if method == "update":
            if not self.observation_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Observation ID must be set when updating an existing observation.",
                        self.observation_id,
                    )
                )
            elif not ObservationModel.objects.filter(id=self.observation_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Observation with ID {self.observation_id} does not exist.",
                        self.observation_id,
                    )
                )

        # Validate foreign key references
        if (
            self.is_member_of_id
            and not ObservationModel.objects.filter(id=self.is_member_of_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Parent observation with ID {self.is_member_of_id} does not exist.",
                    self.is_member_of_id,
                )
            )

        return errors

    def create(self) -> Effect:
        """Create a new Observation."""
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
        """Update an existing Observation."""
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
    "Observation",
    "CodingData",
    "ObservationComponentData",
)
