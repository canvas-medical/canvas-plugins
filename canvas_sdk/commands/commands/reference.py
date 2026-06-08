from uuid import UUID

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class ReferenceCommand(_BaseCommand):
    """A class for managing a Reference command within a specific note."""

    class Meta:
        key = "reference"

    diagnostic_view_id: UUID | None = Field(
        default=None, json_schema_extra={"commands_api_name": "diagnostic_view"}, strict=False
    )


__exports__ = ("ReferenceCommand",)
