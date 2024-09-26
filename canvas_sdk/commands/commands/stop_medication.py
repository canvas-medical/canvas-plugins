from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class StopMedicationCommand(_BaseCommand):
    """A class for managing a StopMedication command within a specific note."""

    class Meta:
        key = "stopMedication"
        commit_required_fields = ("medication_id",)

    # how do we make sure this is a valid medication_id for the patient?
    medication_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "medication"}
    )
    rationale: str | None = None

    @property
    def values(self) -> dict:
        """The StopMedication command's field values."""
        return {"medication_id": self.medication_id, "rationale": self.rationale}
