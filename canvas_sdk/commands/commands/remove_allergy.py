from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class RemoveAllergyCommand(BaseCommand):
    """A class for managing a Remove Allergy command within a specific note."""

    class Meta:
        key = "removeAllergy"
        commit_required_fields = ("allergy_id",)

    allergy_id: str | None = Field(
        description="The external ID of the allergy to remove.",
        default=None,
        json_schema_extra={"commands_api_name": "allergy"},
    )
    narrative: str | None = None

    @property
    def values(self) -> dict:
        """The Remove Allergy command's field values."""
        return {
            "allergy_id": self.allergy_id,
            "narrative": self.narrative,
        }
