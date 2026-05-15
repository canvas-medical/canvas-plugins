from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class ReferenceCommand(_BaseCommand):
    """A class for managing a Reference command within a specific note.

    Embeds the rendered table of a DiagnosticView into the note. Plugins supply the
    DiagnosticView's primary key as ``diagnostic_view_id``; the home-app interpreter
    wraps it into the autocomplete payload shape the SDK schema expects.
    """

    class Meta:
        key = "reference"

    diagnostic_view_id: int | None = Field(
        default=None, json_schema_extra={"commands_api_name": "diagnostic_view"}
    )


__exports__ = ("ReferenceCommand",)
