import datetime
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.note.base import NoteOrAppointmentABC
from canvas_sdk.v1.data import NoteType, Patient
from canvas_sdk.v1.data.note import NoteTypeCategories


class Note(NoteOrAppointmentABC):
    """
    Effect to create a visit note.

    Attributes:
        note_type_id (UUID | str): The ID of the note type.
        datetime_of_service (datetime.datetime): The date and time of the service.
        patient_id (str): The ID of the patient.
    """

    class Meta:
        effect_type = "NOTE"

    note_type_id: UUID | str
    datetime_of_service: datetime.datetime
    patient_id: str

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the note type category and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid note type categories.
        """
        errors = super()._get_error_details(method)

        note_type_category = (
            NoteType.objects.values_list("category", flat=True).filter(id=self.note_type_id).first()
        )

        if not note_type_category:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Note type with ID {self.note_type_id} does not exist.",
                    self.note_type_id,
                )
            )
        elif note_type_category in (
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

        if not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with ID {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        return errors


__exports__ = ("Note",)
