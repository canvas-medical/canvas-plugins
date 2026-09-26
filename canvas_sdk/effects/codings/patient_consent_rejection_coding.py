from canvas_sdk.effects.codings._coding import CodingEffect


class PatientConsentRejectionCoding(CodingEffect):
    """Create, update, or delete a consent rejection reason. ``id`` is its ``dbid``."""

    class Meta:
        effect_type = "PATIENT_CONSENT_REJECTION_CODING"

    _entity_label: str = "patient consent rejection coding"


__exports__ = ("PatientConsentRejectionCoding",)
