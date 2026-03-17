import json
from typing import Any

from pydantic import ValidationError
from pydantic_core import InitErrorDetails

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.patient_group import PatientGroup as PatientGroupModel


class PatientGroup(_BaseEffect):
    """An Effect for managing patient group membership."""

    class Meta:
        apply_required_fields = ("group_id",)

    group_id: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.group_id and not PatientGroupModel.objects.filter(id=self.group_id).exists():
            errors.append(
                self._create_error_detail(
                    "group_id",
                    f"PatientGroup with id: {self.group_id} does not exist.",
                    self.group_id,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """The effect's serializable data."""
        return {"group_id": self.group_id}

    def _effect_payload(self, patient_ids: list[str]) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": {**self.values, "patient_ids": patient_ids}}

    def _validate_patients(self, patient_ids: list[str]) -> None:
        if not patient_ids:
            return
        existing_ids = set(Patient.objects.filter(id__in=patient_ids).values_list("id", flat=True))
        missing = [pid for pid in patient_ids if pid not in existing_ids]
        if missing:
            errors = [
                self._create_error_detail(
                    "patient_id",
                    f"Patient with id: {patient_id} does not exist.",
                    patient_id,
                )
                for patient_id in missing
            ]
            raise ValidationError.from_exception_data(self.__class__.__name__, errors)

    def _apply_effect(self, effect_type: EffectType, patient_ids: list[str]) -> Effect:
        self._validate_before_effect("apply")
        self._validate_patients(patient_ids)
        return Effect(type=effect_type, payload=json.dumps(self._effect_payload(patient_ids)))

    def add_member(self, patient_ids: list[str]) -> Effect:
        """Add patient(s) as members of the group."""
        return self._apply_effect(EffectType.PATIENT_GROUP__ADD_MEMBER, patient_ids)

    def deactivate_member(self, patient_ids: list[str]) -> Effect:
        """Deactivate patient(s) from the group."""
        return self._apply_effect(EffectType.PATIENT_GROUP__DEACTIVATE_MEMBER, patient_ids)


__exports__ = ("PatientGroup",)
