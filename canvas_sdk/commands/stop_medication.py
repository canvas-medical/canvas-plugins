from canvas_sdk.commands.base import _BaseCommand


class StopMedicationCommand(_BaseCommand):
    """A class for managing a StopMedication command within a specific note."""

    # how do we make sure this is a valid medication_id for the patient?
    medication_id: int
    rationale: str | None = None

    @property
    def values(self) -> dict:
        """The StopMedication command's field values."""
        return {"medication_id": self.medication_id, "rationale": self.rationale}
