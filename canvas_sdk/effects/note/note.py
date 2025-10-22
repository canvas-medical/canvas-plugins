import datetime
import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note.base import NoteOrAppointmentABC
from canvas_sdk.v1.data import Note as NoteModel
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

    note_type_id: UUID | str | None = None
    datetime_of_service: datetime.datetime | None = None
    patient_id: str | None = None
    title: str | None = None

    def push_charges(self) -> Effect:
        """Pushes BillingLineItems from the Note to the associated Claim. Identicial to clicking the Push Charges button in the note footer."""
        self._validate_before_effect("push_charges")
        return Effect(
            type="PUSH_NOTE_CHARGES",
            payload=json.dumps({"note": self.instance_id}),
        )

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the note type category and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid note type categories.
        """
        errors = super()._get_error_details(method)

        if method == "push_charges":
            if not self.instance_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'instance_id' is required to push charges from a note to a claim.",
                        None,
                    )
                )
            elif not (note := NoteModel.objects.filter(id=self.instance_id).first()):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note with ID {self.instance_id} does not exist.",
                        self.instance_id,
                    )
                )
            elif not note.note_type_version or not note.note_type_version.is_billable:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note with note type {note.note_type_version} is not billable and has no associated claim.",
                        note.note_type_version,
                    )
                )

            return errors

        if method == "create":
            if not self.note_type_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'note_type_id' is required to create a note.",
                        None,
                    )
                )

            if not self.datetime_of_service:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'datetime_of_service' is required to create a note.",
                        None,
                    )
                )

            if not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'patient_id' is required to create a note.",
                        None,
                    )
                )

            if self.instance_id and NoteModel.objects.filter(id=self.instance_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note with ID {self.instance_id} already exists.",
                        self.instance_id,
                    )
                )

        elif method == "update":
            if self.note_type_id:
                errors.append(
                    self._create_error_detail(
                        "invalid",
                        "Field 'note_type_id' cannot be updated for a note.",
                        self.note_type_id,
                    )
                )
            if self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "invalid",
                        "Field 'patient_id' cannot be updated for a note.",
                        self.patient_id,
                    )
                )

            if self.instance_id and not NoteModel.objects.filter(id=self.instance_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note with ID {self.instance_id} does not exist.",
                        self.instance_id,
                    )
                )

        if self.note_type_id:
            note_type_category = (
                NoteType.objects.values_list("category", flat=True)
                .filter(id=self.note_type_id)
                .first()
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

        if self.patient_id and not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with ID {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        return errors


__exports__ = ("Note",)
