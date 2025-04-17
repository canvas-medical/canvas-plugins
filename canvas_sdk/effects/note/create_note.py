import datetime
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.note.base import CreateNoteOrAppointmentABC
from canvas_sdk.v1.data import NoteType, Patient
from canvas_sdk.v1.data.note import NoteTypeCategories


class CreateNote(CreateNoteOrAppointmentABC):
    """
    Effect to create a visit note.

    Attributes:
        note_type_id (UUID | str): The ID of the note type.
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

        if not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with ID {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        return errors
