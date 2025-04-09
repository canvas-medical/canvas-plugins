import datetime
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import NoteType
from canvas_sdk.v1.data.appointment import AppointmentProgressStatus
from canvas_sdk.v1.data.note import NoteTypeCategories


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


class _CreateNoteOrAppointment(_BaseEffect):
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


class CreateNote(_CreateNoteOrAppointment):
    """
    Effect to create a visit note.

    Attributes:
        datetime_of_service (datetime.datetime): The date and time of the service.
        patient_id (str): The ID of the patient.
    """

    class Meta:
        effect_type = EffectType.CREATE_NOTE

    note_type_id: UUID | str
    datetime_of_service: datetime.datetime
    patient_id: str

    @property
    def values(self) -> dict[str, Any]:
        """
        Returns a dictionary of values for the visit note creation effect.

        Returns:
            dict[str, Any]: A dictionary containing the base values and the datetime of service.
        """
        return {
            **super().values,
            "note_type": str(self.note_type_id),
            "datetime_of_service": self.datetime_of_service.isoformat(),
            "patient": self.patient_id,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the note type category and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid note type categories.
        """
        errors = super()._get_error_details(method)

        note_type_category = NoteType.objects.values_list("category", flat=True).get(
            id=self.note_type_id
        )
        if note_type_category in (
            NoteTypeCategories.APPOINTMENT,
            NoteTypeCategories.SCHEDULE_EVENT,
            NoteTypeCategories.MESSAGE,
            NoteTypeCategories.LETTER,
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Visit note type cannot be of type: {note_type_category}.",
                    self.note_type_id,
                )
            )

        return errors


class CreateAppointment(_CreateNoteOrAppointment):
    """
    Effect to create an appointment.

    Attributes:
        appointment_note_type_id (UUID | str): The ID of the appointment note type.
        start_time (datetime.datetime): The start time of the appointment.
        duration_minutes (int): The duration of the appointment in minutes.
        meeting_link (str | None): The meeting link for the appointment, if any.
        patient_id (str | None): The ID of the patient, if applicable.
        external_identifiers (list[AppointmentIdentifier] | None): A list of external identifiers for the appointment.
        status (AppointmentProgressStatus | None): The status of the appointment.
    """

    class Meta:
        effect_type = EffectType.CREATE_APPOINTMENT

    note_type_id: UUID | str | None = None
    appointment_note_type_id: UUID | str
    start_time: datetime.datetime
    duration_minutes: int
    meeting_link: str | None = None
    patient_id: str | None
    external_identifiers: list[AppointmentIdentifier] | None = None
    status: AppointmentProgressStatus | None = None

    @property
    def values(self) -> dict[str, Any]:
        """
        Returns a dictionary of values for the appointment creation effect.

        Returns:
            dict[str, Any]: A dictionary containing the base values and additional appointment-specific details.
        """
        return {
            **super().values,
            "note_type": str(self.note_type_id) if self.note_type_id else None,
            "appointment_note_type": str(self.appointment_note_type_id),
            "start_time": self.start_time.isoformat(),
            "duration_minutes": self.duration_minutes,
            "meeting_link": self.meeting_link,
            "patient": self.patient_id,
            "status": self.status.value if self.status else None,
            "external_identifiers": [
                {"system": identifier.system, "value": identifier.value}
                for identifier in self.external_identifiers
            ]
            if self.external_identifiers
            else None,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the appointment note type and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid appointment note types or missing patient IDs.
        """
        errors = super()._get_error_details(method)

        valid_appointment_types = (
            NoteTypeCategories.APPOINTMENT,
            NoteTypeCategories.SCHEDULE_EVENT,
        )

        note_type_category = (
            NoteTypeCategories.APPOINTMENT
            if not self.note_type_id
            else NoteType.objects.values_list("category", flat=True).get(id=self.note_type_id)
        )

        if note_type_category not in valid_appointment_types:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Appointment note type must be one of: {valid_appointment_types} but got: {note_type_category}.",
                    self.note_type_id,
                )
            )

        if note_type_category == NoteTypeCategories.APPOINTMENT and not self.patient_id:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Appointment requires a patient_id.",
                    self.note_type_id,
                )
            )

        category, is_scheduleable = NoteType.objects.values_list("category", "is_scheduleable").get(
            id=self.appointment_note_type_id
        )
        if category != NoteTypeCategories.ENCOUNTER:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Appointment note type must be of type, {NoteTypeCategories.ENCOUNTER} but got: {category}.",
                    self.appointment_note_type_id,
                )
            )

        if not is_scheduleable:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Appointment note type must be scheduleable.",
                    self.appointment_note_type_id,
                )
            )
        return errors
