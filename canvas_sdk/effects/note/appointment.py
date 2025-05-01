from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.note.base import AppointmentABC
from canvas_sdk.v1.data import NoteType, Patient
from canvas_sdk.v1.data.note import NoteTypeCategories


class ScheduleEvent(AppointmentABC):
    """
    Effect to create a schedule event.

    Attributes:
        note_type_id (UUID | str): The ID of the note type.
        patient_id (str | None): The ID of the patient, if applicable.
        description (str | None): The description of the schedule event, if applicable.
    """

    class Meta:
        effect_type = "SCHEDULE_EVENT"

    note_type_id: UUID | str
    patient_id: str | None = None
    description: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the schedule event note type and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid schedule event note types.
        """
        errors = super()._get_error_details(method)

        note_type = (
            NoteType.objects.values("category", "is_patient_required", "allow_custom_title")
            .filter(id=self.note_type_id)
            .first()
        )

        if not note_type:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Note type with ID {self.note_type_id} does not exist.",
                    self.note_type_id,
                )
            )
            return errors

        if note_type["category"] != NoteTypeCategories.SCHEDULE_EVENT:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Schedule event note type must be of type: {NoteTypeCategories.SCHEDULE_EVENT}.",
                    self.note_type_id,
                )
            )

        if note_type["is_patient_required"] and not self.patient_id:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Patient ID is required for this note type.",
                    self.note_type_id,
                )
            )

        if not note_type["allow_custom_title"] and self.description:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Description is not allowed for this note type.",
                    self.note_type_id,
                )
            )

        return errors


class Appointment(AppointmentABC):
    """
    Effect to create an appointment.

    Attributes:
        appointment_note_type_id (UUID | str): The ID of the appointment note type.
        meeting_link (str | None): The meeting link for the appointment, if any.
        patient_id (str): The ID of the patient.
    """

    class Meta:
        effect_type = "APPOINTMENT"

    appointment_note_type_id: UUID | str
    meeting_link: str | None = None
    patient_id: str

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


__exports__ = ("ScheduleEvent", "Appointment")
