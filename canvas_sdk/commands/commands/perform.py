from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class PerformCommand(BaseCommand):
    """A class for managing a Perform command within a specific note."""

    class Meta:
        key = "perform"

    cpt_code: str | None = Field(default=None, json_schema_extra={"commands_api_name": "perform"})
    notes: str | None = None


__exports__ = ("PerformCommand",)
