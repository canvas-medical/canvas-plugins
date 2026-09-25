from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.base import _OptionalId
from canvas_sdk.v1.data import Assessment, Condition
from canvas_sdk.v1.data.condition import ClinicalStatus


class RemovePastMedicalHistoryCommand(BaseCommand):
    """A class for managing a RemovePastMedicalHistory command within a specific note."""

    class Meta:
        key = "removePastMedicalHistory"

    condition_id: _OptionalId = Field(
        description="The external ID of the resolved condition to remove from past medical history.",
        default=None,
        json_schema_extra={"commands_api_name": "condition"},
    )
    rationale: str | None = Field(default=None, max_length=512)

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.condition_id is None:
            return errors

        # Both checks off one row. Ownership is judged against every committed condition, so
        # this patient's own non-history condition is not reported as belonging to someone else.
        entry = (
            Condition.objects.committed()
            .filter(id=self.condition_id)
            .values("patient__id", "clinical_status", "surgical")
            .first()
        )

        if entry is None or not self._is_target_patient(entry["patient__id"]):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Condition {self.condition_id} does not belong to this command's patient",
                    self.condition_id,
                )
            )
            return errors

        # The Past Medical History command anchors to a Condition and originates it with a
        # "resolved" clinical status, so that status is what separates history from an active
        # problem. Surgical history is recorded by its own command.
        if entry["clinical_status"] != ClinicalStatus.RESOLVED or entry["surgical"]:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Condition {self.condition_id} is not a past medical history "
                    "entry, so this command cannot remove it",
                    self.condition_id,
                )
            )
            return errors

        # An assessment is a clinician's note against the condition, and withdrawing the
        # condition would leave it describing nothing. The note's picker leaves these out too.
        if Assessment.objects.committed().filter(condition__id=self.condition_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Condition {self.condition_id} has assessments recorded against it, "
                    "so this command cannot remove it",
                    self.condition_id,
                )
            )

        return errors


__exports__ = ("RemovePastMedicalHistoryCommand",)
