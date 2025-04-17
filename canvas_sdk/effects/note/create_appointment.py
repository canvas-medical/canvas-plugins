import datetime
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.note.base import CreateAppointmentABC
from canvas_sdk.v1.data import NoteType, Patient
from canvas_sdk.v1.data.note import NoteTypeCategories


class CreateScheduleEvent(CreateAppointmentABC):
    """
    Effect to create a schedule event.

    Attributes:
        note_type_id (UUID | str): The ID of the note type.
        patient_id (str | None): The ID of the patient, if applicable.
    """

    class Meta:
        effect_type = EffectType.CREATE_SCHEDULE_EVENT

    note_type_id: UUID | str
    patient_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """
        Returns a dictionary of values for the schedule event creation effect.

        Returns:
            dict[str, Any]: A dictionary containing the base values and additional schedule event-specific details.
        """
        return {
            **super().values,
            "note_type": str(self.note_type_id),
            "patient": self.patient_id,
            "external_identifiers": [
                {"system": identifier.system, "value": identifier.value}
                for identifier in self.external_identifiers
            ]
            if self.external_identifiers
            else None,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the schedule event note type and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid schedule event note types.
        """
        errors = super()._get_error_details(method)

        note_type_category = NoteType.objects.values_list("category", flat=True).get(
            id=self.note_type_id
        )
        if note_type_category != NoteTypeCategories.SCHEDULE_EVENT:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Schedule event note type must be of type: {NoteTypeCategories.SCHEDULE_EVENT}.",
                    self.note_type_id,
                )
            )

        return errors


class CreateAppointment(CreateAppointmentABC):
    """
    Effect to create an appointment.

    Attributes:
        appointment_note_type_id (UUID | str): The ID of the appointment note type.
        meeting_link (str | None): The meeting link for the appointment, if any.
        patient_id (str | None): The ID of the patient, if applicable.
        status (AppointmentProgressStatus | None): The status of the appointment.
    """

    class Meta:
        effect_type = EffectType.CREATE_APPOINTMENT

    appointment_note_type_id: UUID | str
    datetime_of_service: datetime.datetime
    meeting_link: str | None = None
    patient_id: str

    @property
    def values(self) -> dict[str, Any]:
        """
        Returns a dictionary of values for the appointment creation effect.

        Returns:
            dict[str, Any]: A dictionary containing the base values and additional appointment-specific details.
        """
        return {
            **super().values,
            "appointment_note_type": str(self.appointment_note_type_id)
            if self.appointment_note_type_id
            else None,
            "datetime_of_service": self.datetime_of_service.isoformat(),
            "meeting_link": self.meeting_link,
            "patient": self.patient_id,
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

        if not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Patient with ID {self.patient_id} does not exist.",
                    self.patient_id,
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
