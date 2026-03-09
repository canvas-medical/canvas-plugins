from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class EnsurePatientInGroup(_BaseEffect):
    """An Effect that ensures one or more patients are members of a group (idempotent)."""

    class Meta:
        effect_type = EffectType.ENSURE_PATIENT_IN_GROUP
        apply_required_fields = ("patient_ids", "group_id")

    patient_ids: list[str] = []
    group_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values."""
        return {}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"patient_ids": self.patient_ids, "group_id": self.group_id}


class EnsurePatientNotInGroup(_BaseEffect):
    """An Effect that ensures one or more patients are not active members of a group (idempotent)."""

    class Meta:
        effect_type = EffectType.ENSURE_PATIENT_NOT_IN_GROUP
        apply_required_fields = ("patient_ids", "group_id")

    patient_ids: list[str] = []
    group_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values."""
        return {}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"patient_ids": self.patient_ids, "group_id": self.group_id}


__exports__ = (
    "EnsurePatientInGroup",
    "EnsurePatientNotInGroup",
)
