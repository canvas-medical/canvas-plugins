from pydantic import Field

from canvas_sdk.commands.commands.refill import RefillCommand


class AdjustPrescriptionCommand(RefillCommand):
    """A class for managing Adjust Prescription command within a specific note."""

    class Meta:
        key = "adjustPrescription"

    new_fdb_code: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "change_medication_to"}
    )

    def _has_fdb_code(self) -> bool:
        """Check if new_fdb_code is provided and non-empty."""
        return self.new_fdb_code is not None and self.new_fdb_code.strip() != ""


__exports__ = ("AdjustPrescriptionCommand",)
