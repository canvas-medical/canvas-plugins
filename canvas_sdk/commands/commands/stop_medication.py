from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class StopMedicationCommand(_BaseCommand):
    """A class for managing a StopMedication command within a specific note."""

    class Meta:
        key = "stopMedication"

    # how do we make sure this is a valid medication_id for the patient?
    medication_id: str = Field(json_schema_extra={"commands_api_name": "medication"})
    rationale: str | None = None

    @property
    def values(self) -> dict:
        """The StopMedication command's field values."""
        return {"medication_id": self.medication_id, "rationale": self.rationale}


class StopMedicationCommandNoInitValidation:
    """Stop Medication Command without validation on initialization."""

    def __new__(cls, **kwargs: dict) -> StopMedicationCommand:
        """Returns an initialized Stop Medication Command without any validation."""
        return StopMedicationCommand.model_construct(**kwargs)
