from typing import Any
from uuid import UUID

from canvas_sdk.effects.metadata import BaseMetadata
from canvas_sdk.v1.data import Note


class _NoteMetadata(BaseMetadata):
    """Effect to upsert a Note Metadata record."""

    class Meta:
        effect_type = "NOTE_METADATA"

    note_id: UUID | str

    def _get_error_details(self, method: Any) -> list:
        errors = super()._get_error_details(method)

        if not Note.objects.filter(id=self.note_id).exists():
            errors.append(
                self._create_error_detail(
                    "note_id",
                    f"Note with id: {self.note_id} does not exist.",
                    self.note_id,
                )
            )

        return errors


__exports__ = ()
