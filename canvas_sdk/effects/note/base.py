import datetime
import json
from abc import ABC
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.v1.data import PracticeLocation, Staff
from canvas_sdk.v1.data.appointment import Appointment, AppointmentProgressStatus


@dataclass
class AppointmentIdentifier:
    """
    Dataclass for appointment identifiers.

    Attributes:
        system (str): The system identifier for the appointment.
        value (str): The value associated with the system identifier.
    """

    system: str
    value: str


class NoteOrAppointmentABC(TrackableFieldsModel, ABC):
    """
    Base class for all note effects.

    Attributes:
        instance_id (UUID | str): The unique identifier for the note or appointment instance.
        practice_location_id (UUID | str): The ID of the practice location.
        provider_id (str): The ID of the provider.
    """

    class Meta:
        effect_type = None

    instance_id: UUID | str | None = None
    practice_location_id: UUID | str | None = None
    provider_id: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the practice location and provider IDs and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid practice location or provider IDs.
        """
        errors = super()._get_error_details(method)

        if method == "create":
            if self.instance_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Instance ID should not be provided for create effects.",
                        self.instance_id,
                    )
                )
            if not self.practice_location_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Practice location ID is required.",
                        self.practice_location_id,
                    )
                )
            if not self.provider_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Provider ID is required.",
                        self.provider_id,
                    )
                )

        else:
            if not self.instance_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'instance_id' is required to update or cancel/delete a note or appointment.",
                        None,
                    )
                )

        if (
            self.practice_location_id
            and not PracticeLocation.objects.filter(id=self.practice_location_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Practice location with ID {self.practice_location_id} does not exist.",
                    self.practice_location_id,
                )
            )

        if self.provider_id and not Staff.objects.filter(id=self.provider_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Provider with ID {self.provider_id} does not exist.",
                    self.provider_id,
                )
            )

        return errors

    def create(self) -> Effect:
        """Send a CREATE effect for the note or appointment."""
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
        """Send an UPDATE effect for the note or appointment."""
        self._validate_before_effect("update")

        # Check if any fields were actually modified
        if self._dirty_keys == {"instance_id"}:
            raise ValueError("No fields have been modified. Nothing to update.")

        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


class AppointmentABC(NoteOrAppointmentABC, ABC):
    """
    Base class for appointment create/update effects.

    Attributes:
        start_time (datetime.datetime): The start time of the appointment.
        duration_minutes (int): The duration of the appointment in minutes.
        status (AppointmentProgressStatus | None): The status of the appointment.
        external_identifiers (list[AppointmentIdentifier] | None): List of external identifiers for the appointment.
    """

    class Meta:
        effect_type = "APPOINTMENT"

    _dirty_excluded_keys = [
        "external_identifiers",
    ]

    start_time: datetime.datetime | None = None
    duration_minutes: int | None = None
    status: AppointmentProgressStatus | None = None
    external_identifiers: list[AppointmentIdentifier] | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validates the appointment instance and returns a list of error details if validation fails."""
        errors = super()._get_error_details(method)

        if method == "create":
            # Additional required fields for appointment creation
            if not self.start_time:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'start_time' is required to create an appointment.",
                        None,
                    )
                )

            if not self.duration_minutes:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'duration_minutes' is required to create an appointment.",
                        None,
                    )
                )

        # Validate appointment exists for update/delete
        else:
            if self.instance_id and not Appointment.objects.filter(id=self.instance_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Appointment with ID {self.instance_id} does not exist.",
                        self.instance_id,
                    )
                )

        return errors

    @property
    def values(self) -> dict:
        """
        Returns a dictionary of modified attributes with type-specific transformations.
        """
        values = super().values

        # Handle external_identifiers separately since it's excluded from dirty tracking
        # because it can be a complex type
        # Only include if explicitly set (not None)
        if self.external_identifiers is not None:
            values["external_identifiers"] = [
                {"system": identifier.system, "value": identifier.value}
                for identifier in self.external_identifiers
            ]

        return values


__exports__ = ("AppointmentIdentifier", "NoteOrAppointmentABC", "AppointmentABC")
