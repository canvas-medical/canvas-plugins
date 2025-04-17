from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class SendSurescriptsEligibilityRequestEffect(_BaseEffect):
    """
    An Effect that will send a Surescripts eligibility request.
    """

    class Meta:
        effect_type = EffectType.SEND_SURESCRIPTS_ELIGIBILITY_REQUEST
        apply_required_fields = ("patient_id", "staff_id")

    patient_id: str | None = None
    staff_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Eligibility Request values."""
        return {
            "patient_id": self.patient_id,
            "staff_id": self.staff_id,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """Eligibility Request effect payload."""
        return self.values


class SendSurescriptsMedicationHistoryRequestEffect(_BaseEffect):
    """
    An effect that sends a Surescripts Medication History Request.
    """

    class Meta:
        effect_type = EffectType.SEND_SURESCRIPTS_MEDICATION_HISTORY_REQUEST
        apply_required_fields = ("patient_id", "staff_id")

    patient_id: str | None = None
    staff_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Medication History Request values."""
        return {
            "patient_id": self.patient_id,
            "staff_id": self.staff_id,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """Medication History Request effect payload."""
        return self.values


class SendSurescriptsBenefitsRequestEffect(_BaseEffect):
    """
    An effect that sends a Surescripts Benefits Request.
    """

    class Meta:
        effect_type = EffectType.SEND_SURESCRIPTS_BENEFITS_REQUEST
        apply_required_fields = (
            "patient_id",
            "staff_id",
            "medication_description",
            "medication_ndc",
            "plan",
        )

    patient_id: str | None = None
    staff_id: str | None = None
    medication_description: str | None = None
    medication_ndc: str | None = None
    plan: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Benefits Request values."""
        return {
            "patient_id": self.patient_id,
            "staff_id": self.staff_id,
            "medication_description": self.medication_description,
            "medication_ndc": self.medication_ndc,
            "plan": self.plan,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """Benefits Request effect payload."""
        return self.values


__exports__ = (
    "SendSurescriptsBenefitsRequestEffect",
    "SendSurescriptsEligibilityRequestEffect",
    "SendSurescriptsMedicationHistoryRequestEffect",
)
