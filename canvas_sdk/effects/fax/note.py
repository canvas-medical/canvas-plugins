from typing import Literal
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.fax.base import BaseFaxEffect
from canvas_sdk.v1.data import Note


class FaxNoteEffect(BaseFaxEffect):
    """Fax note effect."""

    class Meta:
        effect_type = EffectType.FAX_NOTE

    note_id: str | UUID

    def _get_error_details(self, method: Literal["apply"]) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if self.note_id and not Note.objects.filter(id=self.note_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Note with ID {self.note_id} does not exist.",
                    self.note_id,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, str]:
        """Return the values of the note fax effect."""
        values = super().values
        return {
            **values,
            "note_id": str(self.note_id),
        }


__exports__ = ()
