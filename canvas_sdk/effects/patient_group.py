from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class EnsurePatientInGroup(_BaseEffect):
    """An Effect that ensures a patient is a member of a group (idempotent)."""

    class Meta:
        effect_type = EffectType.ENSURE_PATIENT_IN_GROUP
        apply_required_fields = ("patient_id", "group_id")

    patient_id: str | None = None
    group_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values."""
        return {}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"patient_id": self.patient_id, "group_id": self.group_id}


class EnsurePatientNotInGroup(_BaseEffect):
    """An Effect that ensures a patient is not an active member of a group (idempotent)."""

    class Meta:
        effect_type = EffectType.ENSURE_PATIENT_NOT_IN_GROUP
        apply_required_fields = ("patient_id", "group_id")

    patient_id: str | None = None
    group_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values."""
        return {}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"patient_id": self.patient_id, "group_id": self.group_id}


__exports__ = (
    "EnsurePatientInGroup",
    "EnsurePatientNotInGroup",
)
