import datetime
from abc import ABC
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import _BaseEffect
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


class CreateNoteOrAppointmentABC(_BaseEffect, ABC):
    """
    Base class for all note creation effects.

    Attributes:
        practice_location_id (UUID | str): The ID of the practice location.
        provider_id (str): The ID of the provider.
    """

    practice_location_id: UUID | str
    provider_id: str

    @property
    def values(self) -> dict[str, Any]:
        """
        Returns a dictionary of values for the note creation effect.

        Returns:
            dict[str, Any]: A dictionary containing the practice location, provider, patient, and note type IDs.
        """
        return {
            "practice_location": str(self.practice_location_id),
            "provider": self.provider_id,
        }

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


class CreateAppointmentABC(CreateNoteOrAppointmentABC, ABC):
    """
    Base class for appointment creation effects.

    Attributes:
        start_time (datetime.datetime): The start time of the appointment.
        duration_minutes (int): The duration of the appointment in minutes.
        status (AppointmentProgressStatus | None): The status of the appointment.
        external_identifiers (list[AppointmentIdentifier] | None): List of external identifiers for the appointment.
    """

    start_time: datetime.datetime
    duration_minutes: int
    status: AppointmentProgressStatus | None = None
    external_identifiers: list[AppointmentIdentifier] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """
        Returns a dictionary of values for the appointment creation effect.

        Returns:
            dict[str, Any]: A dictionary containing the base values and additional appointment-specific details.
        """
        return {
            **super().values,
            "start_time": self.start_time.isoformat(),
            "duration_minutes": self.duration_minutes,
            "status": self.status.value if self.status else None,
            "external_identifiers": [
                {"system": identifier.system, "value": identifier.value}
                for identifier in self.external_identifiers
            ]
            if self.external_identifiers
            else None,
        }
