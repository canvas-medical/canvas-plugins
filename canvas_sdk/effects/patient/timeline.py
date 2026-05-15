from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import _BaseEffect
from canvas_sdk.v1.data import NoteType


class PatientTimelineEffect(_BaseEffect):
    """Effect to configure a patient's timeline, such as excluding specific note types."""

    class Meta:
        effect_type = EffectType.PATIENT_TIMELINE__CONFIGURATION

    excluded_note_types: list[UUID | str]

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.excluded_note_types:
            requested_ids = {str(nt) for nt in self.excluded_note_types}
            existing_ids = {
                str(existing_note_type)
                for existing_note_type in NoteType.objects.filter(
                    unique_identifier__in=requested_ids
                ).values_list("unique_identifier", flat=True)
            }
            missing_ids = requested_ids - existing_ids

            for note_type in missing_ids:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note type '{note_type}' not found.",
                        self.excluded_note_types,
                    )
                )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the note types to exclude."""
        return {"excluded_note_types": [str(nt) for nt in self.excluded_note_types]}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("PatientTimelineEffect",)
