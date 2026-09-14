from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand, _OptionalId
from canvas_sdk.v1.data import Assessment

#: The link is only supplied when a command is written, so those are the only methods worth
#: checking. A commit, delete or enter-in-error addresses a command that already holds whatever
#: link it has.
ASSESSMENT_VALIDATED_METHODS = frozenset({"originate", "edit"})


class _AssessmentLinkedCommand(_BaseCommand):
    """A base class for commands that can be linked to an Assessment made in the same note."""

    class Meta:
        abstract = True

    assessment_id: _OptionalId = Field(
        default=None, json_schema_extra={"commands_api_name": "assessment"}
    )

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Check that the linked assessment was made in the note this command is written in."""
        errors = super()._get_error_details(method)

        if self.assessment_id is None or method not in ASSESSMENT_VALIDATED_METHODS:
            # Nothing of this class's to check. The field is optional, so a command that omits
            # it, or that is being committed or deleted, carries no link to disagree with.
            return errors

        note_id = self._anchor_note_id()

        if note_id is None:
            # The note is not persisted yet, which is ordinary rather than an error: one handler
            # can return `[note.create(...), command.originate(note_uuid=...)]`, and the note
            # only exists once the earlier effect is applied. The interpreter checks the link
            # against the note server-side, by which time both exist.
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
