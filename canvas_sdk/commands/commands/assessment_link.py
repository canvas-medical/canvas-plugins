from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand, _OptionalId
from canvas_sdk.v1.data import Assessment


class _AssessmentLinkedCommand(_BaseCommand):
    """A base class for commands that can be linked to an Assessment made in the same note."""

    class Meta:
        abstract = True

    assessment_id: _OptionalId = Field(
        default=None, json_schema_extra={"commands_api_name": "assessment"}
    )

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Check that the linked assessment was made in the note this command is written in.

        The note is resolved from the command's own note or, on an edit, from the command itself.
        When neither is persisted yet there is nothing to compare against and the check is skipped,
        so a plugin returning several effects at once still works.
        """
        errors = super()._get_error_details(method)

        if self.assessment_id is None or (note_id := self._anchor_note_id()) is None:
            return errors

        if not Assessment.objects.filter(id=self.assessment_id, note__id=note_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Assessment {self.assessment_id} was not made in this command's note.",
                    self.assessment_id,
                )
            )

        return errors


__exports__ = ()
