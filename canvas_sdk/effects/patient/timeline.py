from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import _BaseEffect
from canvas_sdk.v1.data import NoteType


class PatientTimelineEffect(_BaseEffect):
    """
    Effect to configure which note types a patient's chart shows and offers.

    ``excluded_note_types`` hides existing notes of those types from the timeline, and also
    removes them from the New Note button, the timeline's note type filter, and permalink
    access. Exclusions from several plugins are combined.

    ``allowed_new_note_types`` restricts note *creation* only: it is an allow-list of the
    note types the New Note button may offer, leaving the patient's history visible and
    filterable. ``None`` means no constraint; an empty list offers nothing, which hides the
    button. Allow-lists from several plugins are intersected, so a permissive plugin cannot
    widen what a more restrictive one permits.
    """

    class Meta:
        effect_type = EffectType.PATIENT_TIMELINE__CONFIGURATION

    excluded_note_types: list[UUID | str] = []
    allowed_new_note_types: list[UUID | str] | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        requested_ids = {str(nt) for nt in self.excluded_note_types}
        requested_ids |= {str(nt) for nt in self.allowed_new_note_types or []}

        if requested_ids:
            existing_ids = {
                str(existing_note_type)
                for existing_note_type in NoteType.objects.filter(
                    unique_identifier__in=requested_ids
                ).values_list("unique_identifier", flat=True)
            }

            for note_type in requested_ids - existing_ids:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note type '{note_type}' not found.",
                        note_type,
                    )
                )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the note types to exclude, and those the New Note button may offer."""
        return {
            "excluded_note_types": [str(nt) for nt in self.excluded_note_types],
            # None and [] mean different things: no constraint versus allow nothing.
            "allowed_new_note_types": (
                None
                if self.allowed_new_note_types is None
                else [str(nt) for nt in self.allowed_new_note_types]
            ),
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("PatientTimelineEffect",)
