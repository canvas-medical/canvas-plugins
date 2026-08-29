from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand, _OptionalId
from canvas_sdk.v1.data import Medication


class StopMedicationCommand(_BaseCommand):
    """A class for managing a StopMedication command within a specific note."""

    class Meta:
        key = "stopMedication"

    medication_id: _OptionalId = Field(
        default=None, json_schema_extra={"commands_api_name": "medication"}
    )
    rationale: str | None = None

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.medication_id is None:
            return errors

        medication_patient_id = (
            Medication.objects.filter(id=self.medication_id)
            .values_list("patient__id", flat=True)
            .first()
        )

        if medication_patient_id is None or not self._is_target_patient(medication_patient_id):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Medication {self.medication_id} does not belong to this command's patient",
                    self.medication_id,
                )
            )

        return errors


__exports__ = ("StopMedicationCommand",)
