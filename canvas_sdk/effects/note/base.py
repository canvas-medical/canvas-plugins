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
from canvas_sdk.v1.data.appointment import AppointmentProgressStatus


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
        practice_location_id (UUID | str): The ID of the practice location.
        provider_id (str): The ID of the provider.
    """

    class Meta:
        effect_type = None

    practice_location_id: UUID | str
    provider_id: str

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the practice location and provider IDs and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid practice location or provider IDs.
        """
        errors = super()._get_error_details(method)

        if not PracticeLocation.objects.filter(id=self.practice_location_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Practice location with ID {self.practice_location_id} does not exist.",
                    self.practice_location_id,
                )
            )

        if not Staff.objects.filter(id=self.provider_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Provider with ID {self.provider_id} does not exist.",
                    self.provider_id,
                )
            )

        return errors

    def create(self) -> Effect:
        """Originate a new command in the note body."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


class AppointmentABC(NoteOrAppointmentABC, ABC):
    """
    Base class for appointment creation effects.

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

    start_time: datetime.datetime
    duration_minutes: int
    status: AppointmentProgressStatus | None = None
    external_identifiers: list[AppointmentIdentifier] | None = None

    @property
    def values(self) -> dict:
        """
        Returns a dictionary of modified attributes with type-specific transformations.
        """
        values = super().values

        if self.external_identifiers:
            values["external_identifiers"] = [
                {"system": identifier.system, "value": identifier.value}
                for identifier in self.external_identifiers
            ]

        return values


__exports__ = ("AppointmentIdentifier", "NoteOrAppointmentABC", "AppointmentABC")
