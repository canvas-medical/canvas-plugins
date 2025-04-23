from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class ChangeMedicationCommand(BaseCommand):
    """A class for managing a ChangeMedication command within a specific note."""

    class Meta:
        key = "changeMedication"
        commit_required_fields = ("medication_id",)

    medication_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "medication"}
    )
    sig: str | None = None


__exports__ = ("ChangeMedicationCommand",)
