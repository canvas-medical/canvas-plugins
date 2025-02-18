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
