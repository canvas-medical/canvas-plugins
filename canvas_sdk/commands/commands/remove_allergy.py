from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class RemoveAllergyCommand(BaseCommand):
    """A class for managing a Remove Allergy command within a specific note."""

    class Meta:
        key = "removeAllergy"

    allergy_id: str | None = Field(
        description="The external ID of the allergy to remove.",
        default=None,
        json_schema_extra={"commands_api_name": "allergy"},
    )
    narrative: str | None = None


__exports__ = ("RemoveAllergyCommand",)
