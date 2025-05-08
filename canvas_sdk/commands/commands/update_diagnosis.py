from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class UpdateDiagnosisCommand(BaseCommand):
    """A class for managing an Update Diagnosis command within a specific note."""

    class Meta:
        key = "updateDiagnosis"

    condition_code: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "condition"}
    )
    new_condition_code: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "new_condition"}
    )
    background: str | None = None
    narrative: str | None = None


__exports__ = ("UpdateDiagnosisCommand",)
