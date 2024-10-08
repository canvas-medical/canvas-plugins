from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class UpdateDiagnosisCommand(BaseCommand):
    """A class for managing an Update Diagnosis command within a specific note."""

    class Meta:
        key = "updateDiagnosis"
        commit_required_fields = (
            "condition_code",
            "new_condition_code",
        )

    condition_code: str | None = None
    new_condition_code: str | None = None
    background: str | None = None
    narrative: str | None = None

    @property
    def values(self) -> dict:
        """The Update Diagnosis command's field values."""
        return {
            "condition_code": self.condition_code,
            "new_condition_code": self.new_condition_code,
            "background": self.background,
            "narrative": self.narrative,
        }
