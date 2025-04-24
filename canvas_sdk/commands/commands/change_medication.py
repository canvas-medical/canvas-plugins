from typing import Literal

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.v1.data import Medication, Note


class ChangeMedicationCommand(BaseCommand):
    """A class for managing a ChangeMedication command within a specific note."""

    class Meta:
        key = "changeMedication"
        commit_required_fields = ("medication_id",)

    medication_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "medication"}
    )
    sig: str | None = None

    def _get_error_details(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        note = None

        if self.note_uuid:
            note = Note.objects.filter(id=self.note_uuid).first()

            if not note:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"note with id {self.note_uuid} not found.",
                        self.note_uuid,
                    )
                )

        if self.medication_id and note:
            medication = Medication.objects.filter(
                id=self.medication_id, patient=note.patient
            ).first()

            if not medication:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Medication with Id {self.medication_id} not found or not associated with the patient.",
                        self.medication_id,
                    )
                )

        return errors


__exports__ = ("ChangeMedicationCommand",)
