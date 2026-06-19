from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect, EffectType, _BaseEffect
from canvas_sdk.v1.data import Note, Patient


class _ReloadActionButtonsEffect(_BaseEffect):
    """Actual ReloadActionButtons effect."""

    class Meta:
        effect_type = EffectType.RELOAD_ACTION_BUTTONS

    note_id: str | None = None
    patient_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The reload effect's wire values."""
        return {"note_id": self.note_id, "patient_id": self.patient_id}


class ReloadNoteActionButtonsEffect(Model):
    """Reload a note's action buttons effect."""

    id: str

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if self.id and not Note.objects.filter(id=self.id).exists():
            errors.append(
                self._create_error_detail(
                    "value", f"Note with ID {self.id} does not exist.", self.id
                )
            )
        return errors

    def apply(self) -> Effect:
        """Validate the note subject and reload its buttons."""
        self._validate_before_effect("apply")
        return _ReloadActionButtonsEffect(note_id=self.id).apply()


class ReloadPatientActionButtonsEffect(Model):
    """Reload a patient's action buttons effect."""

    id: str

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if self.id and not Patient.objects.filter(id=self.id).exists():
            errors.append(
                self._create_error_detail(
                    "value", f"Patient with ID {self.id} does not exist.", self.id
                )
            )
        return errors

    def apply(self) -> Effect:
        """Validate the patient subject and reload its buttons."""
        self._validate_before_effect("apply")
        return _ReloadActionButtonsEffect(patient_id=self.id).apply()


__exports__ = ("ReloadNoteActionButtonsEffect", "ReloadPatientActionButtonsEffect")
