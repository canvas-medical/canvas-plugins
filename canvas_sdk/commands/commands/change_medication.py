from typing import Literal
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.v1.data import Medication


class ChangeMedicationCommand(BaseCommand):
    """A class for managing a ChangeMedication command within a specific note."""

    class Meta:
        key = "changeMedication"
        commit_required_fields = ("medication_id",)

    medication_id: UUID | None = Field(
        default=None, json_schema_extra={"commands_api_name": "medication"}
    )
    sig: str | None = None

    def _get_error_details(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> list[InitErrorDetails]:
        """Check that the medication being changed is one this patient actually has."""
        errors = super()._get_error_details(method)

        if not self.medication_id or (patient_id := self._anchor_patient_id()) is None:
            return errors

        if (
            not Medication.objects.active()
            .filter(id=self.medication_id, patient__id=patient_id)
            .exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Medication with Id {self.medication_id} not found or not associated with the patient.",
                    self.medication_id,
                )
            )

        return errors


__exports__ = ("ChangeMedicationCommand",)
