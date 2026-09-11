from canvas_sdk.effects.codings._base import CodingCrudEffect


class PatientConsentCoding(CodingCrudEffect):
    """Effect to create/update/delete a Patient Consent coding entry."""

    class Meta:
        effect_type = "PATIENT_CONSENT_CODING"

    _entity_label: str = "patient consent coding"


__exports__ = ("PatientConsentCoding",)
