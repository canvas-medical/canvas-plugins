"""
Typed wrappers for SURESCRIPTS_*_RESPONSE event payloads.

Plugins receive these as the `context` of an `Event` whose `type` is
`EventType.SURESCRIPTS_ELIGIBILITY_RESPONSE` or
`EventType.SURESCRIPTS_BENEFITS_RESPONSE`. The home-app interpreter populates
the context with a sanitized payload — never raw X12 / protocol data — and
echoes the `correlation_id` from the originating request effect.
"""

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class EligibilityPlan:
    """A single plan returned in a Surescripts eligibility response."""

    pbm_name: str
    payer_id: str
    member_id: str
    plan_network_id: str | None
    group_number: str | None
    drug_formulary_number: str | None
    coverage_id: str | None
    description: str | None
    rejected: bool
    reject_reason: str | None
    service_types: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EligibilityPlan":
        """Build an EligibilityPlan from a dict in the event context."""
        return cls(
            pbm_name=data.get("pbm_name", ""),
            payer_id=data.get("payer_id", ""),
            member_id=data.get("member_id", ""),
            plan_network_id=data.get("plan_network_id"),
            group_number=data.get("group_number"),
            drug_formulary_number=data.get("drug_formulary_number"),
            coverage_id=data.get("coverage_id"),
            description=data.get("description"),
            rejected=bool(data.get("rejected", False)),
            reject_reason=data.get("reject_reason"),
            service_types=list(data.get("service_types") or []),
        )


@dataclasses.dataclass(frozen=True)
class SurescriptsEligibilityResponse:
    """Sanitized payload of a SURESCRIPTS_ELIGIBILITY_RESPONSE event."""

    correlation_id: str
    patient_id: str
    plans: list[EligibilityPlan]
    error: str | None

    @classmethod
    def from_context(cls, context: dict[str, Any]) -> "SurescriptsEligibilityResponse":
        """Parse the event.context dict produced by home-app's interpreter."""
        return cls(
            correlation_id=context.get("correlation_id", ""),
            patient_id=context.get("patient_id", ""),
            plans=[EligibilityPlan.from_dict(p) for p in context.get("plans") or []],
            error=context.get("error"),
        )


@dataclasses.dataclass(frozen=True)
class TherapeuticAlternative:
    """A formulary alternative medication returned in a Surescripts benefits response."""

    ndc: str
    description: str | None
    brand_or_generic: str | None
    rx_or_otc: str | None
    formulary_status: str | None
    copays: list[str]
    prior_authorization_required: bool
    step_therapy_required: bool
    quantity_limits: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TherapeuticAlternative":
        """Build a TherapeuticAlternative from a dict in the event context."""
        return cls(
            ndc=data.get("ndc", ""),
            description=data.get("description"),
            brand_or_generic=data.get("brand_or_generic"),
            rx_or_otc=data.get("rx_or_otc"),
            formulary_status=data.get("formulary_status"),
            copays=list(data.get("copays") or []),
            prior_authorization_required=bool(data.get("prior_authorization_required", False)),
            step_therapy_required=bool(data.get("step_therapy_required", False)),
            quantity_limits=list(data.get("quantity_limits") or []),
        )


@dataclasses.dataclass(frozen=True)
class BenefitCoverage:
    """Formulary and coverage detail for one plan in a Surescripts benefits response."""

    pbm_name: str
    payer_id: str
    formulary_status: str | None
    prior_authorization_required: bool
    step_therapy_required: bool
    quantity_limits: list[str]
    copays: list[str]
    alternatives: list[TherapeuticAlternative]
    rejected: bool
    reject_reason: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BenefitCoverage":
        """Build a BenefitCoverage from a dict in the event context."""
        return cls(
            pbm_name=data.get("pbm_name", ""),
            payer_id=data.get("payer_id", ""),
            formulary_status=data.get("formulary_status"),
            prior_authorization_required=bool(data.get("prior_authorization_required", False)),
            step_therapy_required=bool(data.get("step_therapy_required", False)),
            quantity_limits=list(data.get("quantity_limits") or []),
            copays=list(data.get("copays") or []),
            alternatives=[
                TherapeuticAlternative.from_dict(a) for a in data.get("alternatives") or []
            ],
            rejected=bool(data.get("rejected", False)),
            reject_reason=data.get("reject_reason"),
        )


@dataclasses.dataclass(frozen=True)
class SurescriptsBenefitsResponse:
    """Sanitized payload of a SURESCRIPTS_BENEFITS_RESPONSE event."""

    correlation_id: str
    patient_id: str
    medication_ndc: str
    coverages: list[BenefitCoverage]
    error: str | None

    @classmethod
    def from_context(cls, context: dict[str, Any]) -> "SurescriptsBenefitsResponse":
        """Parse the event.context dict produced by home-app's interpreter."""
        return cls(
            correlation_id=context.get("correlation_id", ""),
            patient_id=context.get("patient_id", ""),
            medication_ndc=context.get("medication_ndc", ""),
            coverages=[BenefitCoverage.from_dict(c) for c in context.get("coverages") or []],
            error=context.get("error"),
        )


__exports__ = (
    "BenefitCoverage",
    "EligibilityPlan",
    "SurescriptsBenefitsResponse",
    "SurescriptsEligibilityResponse",
    "TherapeuticAlternative",
)
