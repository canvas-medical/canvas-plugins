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


class SurescriptsBenefitsCoordinationOverride(_BaseEffect):
    """Override BenefitsCoordination fields on the outbound Surescripts NewRx.
    Returned by a handler of `EventType.PRESCRIBE_COMMAND__PRE_SEND`.

    Any field left as None is treated as "no override" — pharmacy falls through
    to the value derived from the Surescripts eligibility response for that
    field. A plugin can override a single value without disturbing the others.
    When an override is present, it wins over the eligibility-derived value, and
    the BenefitsCoordination segment is included even when no eligibility lookup
    was performed.

    Field semantics (NCPDP SCRIPT BenefitsCoordination):
      - `iin_number`: PayerIdentification IINumber (BIN).
      - `processor_identification_number`: PayerIdentification PCN.
      - `group_id`: BenefitsCoordination GroupID.
      - `pbm_member_id`: BenefitsCoordination PBMMemberID (Member ID).
    """

    class Meta:
        effect_type = EffectType.SURESCRIPTS_BENEFITS_COORDINATION_OVERRIDE

    iin_number: str | None = None
    processor_identification_number: str | None = None
    group_id: str | None = None
    pbm_member_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Only include fields the plugin set; absent keys mean 'no override'."""
        return {
            key: value
            for key, value in (
                ("iin_number", self.iin_number),
                ("processor_identification_number", self.processor_identification_number),
                ("group_id", self.group_id),
                ("pbm_member_id", self.pbm_member_id),
            )
            if value is not None
        }


__exports__ = (
    "SendSurescriptsBenefitsRequestEffect",
    "SendSurescriptsEligibilityRequestEffect",
    "SendSurescriptsMedicationHistoryRequestEffect",
    "SurescriptsBenefitsCoordinationOverride",
)
