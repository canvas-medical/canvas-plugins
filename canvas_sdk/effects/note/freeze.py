from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.v1.data import Note, Staff


class _FreezeNoteEffect(_BaseEffect):
    """
    Freezes a note to prevent modifications for a specified duration.

    This effect sets `related_data.freeze = True` on the note, which displays
    a banner in the UI and prevents edits. The note will be automatically
    unfrozen after the specified duration.

    Attributes:
        note_id: The UUID of the note to freeze.
        duration: The freeze duration in seconds (default: 300, minimum: 1).
        user_id: The staff key of the user who initiated the freeze (optional).
                 If provided, this user will still be able to edit the note.
        blur: Whether to blur the note content for other users (default: False).
    """

    class Meta:
        effect_type = EffectType.FREEZE_NOTE

    note_id: UUID | str = Field(description="The note's id")
    duration: int = Field(default=300, ge=1, description="Freeze duration in seconds")
    user_id: str | None = Field(
        default=None,
        description="Staff key of user who initiated the freeze (can still edit)",
    )
    blur: bool = Field(
        default=False,
        description="Whether to blur the note content for other users",
    )

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate that the note and staff exist."""
        errors = super()._get_error_details(method)

        if not Note.objects.filter(id=self.note_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Note with ID {self.note_id} does not exist.",
                    self.note_id,
                )
            )

        if self.user_id and not Staff.objects.filter(id=self.user_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Staff with ID {self.user_id} does not exist.",
                    self.user_id,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the effect payload values."""
        result = {
            "note_id": str(self.note_id),
            "duration": self.duration,
            "blur": self.blur,
        }
        if self.user_id:
            result["user_id"] = self.user_id
        return result


class _UnfreezeNoteEffect(_BaseEffect):
    """
    Unfreezes a note to allow modifications.

    This effect sets `related_data.freeze = False` on the note, removing
    the freeze banner and allowing edits again.

    Attributes:
        note_id: The UUID of the note to unfreeze.
    """

    class Meta:
        effect_type = EffectType.UNFREEZE_NOTE

    note_id: UUID | str = Field(description="The note's id")

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate that the note exists."""
        errors = super()._get_error_details(method)

        if not Note.objects.filter(id=self.note_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Note with ID {self.note_id} does not exist.",
                    self.note_id,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the effect payload values."""
        return {
            "note_id": str(self.note_id),
        }


__exports__ = ()
