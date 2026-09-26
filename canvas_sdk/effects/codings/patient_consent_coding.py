from enum import StrEnum

from pydantic import Field

from canvas_sdk.effects.codings._coding import CodingEffect


class ConsentExpirationRule(StrEnum):
    """When a patient's consent of this type expires."""

    NEVER = "never"
    IN_ONE_YEAR = "in_one_year"
    END_OF_YEAR = "end_of_year"


class PatientConsentCoding(CodingEffect):
    """Create, update, or delete a patient consent type. ``id`` is its ``dbid``."""

    class Meta:
        effect_type = "PATIENT_CONSENT_CODING"

    _entity_label: str = "patient consent coding"
    _create_required: tuple[str, ...] = ("system", "display", "expiration_rule")

    expiration_rule: ConsentExpirationRule | None = Field(default=None, strict=False)
    is_mandatory: bool | None = None
    is_proof_required: bool | None = None
    show_in_patient_portal: bool | None = None
    summary: str | None = None


__exports__ = ("ConsentExpirationRule", "PatientConsentCoding")
