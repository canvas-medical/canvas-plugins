from canvas_sdk.effects.codings._base import CodingCrudEffect


class PatientConsentRejectionCoding(CodingCrudEffect):
    """Effect to create/update/delete a Patient Consent Rejection coding entry."""

    class Meta:
        effect_type = "PATIENT_CONSENT_REJECTION_CODING"

    _entity_label: str = "patient consent rejection coding"


__exports__ = ("PatientConsentRejectionCoding",)
