from canvas_sdk.events.surescripts.surescripts_messages import (
    BenefitCoverage,
    EligibilityPlan,
    SurescriptsBenefitsResponse,
    SurescriptsEligibilityResponse,
    TherapeuticAlternative,
)


def test_eligibility_plan_from_dict_full_payload() -> None:
    """A fully populated plan dict round-trips into an EligibilityPlan dataclass."""
    plan = EligibilityPlan.from_dict(
        {
            "pbm_name": "Acme PBM",
            "payer_id": "PAYER1",
            "member_id": "MEM-42",
            "plan_network_id": "NET1",
            "group_number": "GRP1",
            "drug_formulary_number": "FORM1",
            "coverage_id": "COV1",
            "description": "Acme Premier",
            "rejected": False,
            "reject_reason": None,
            "service_types": ["MEDICAL", "RX"],
        }
    )

    assert plan.pbm_name == "Acme PBM"
    assert plan.payer_id == "PAYER1"
    assert plan.member_id == "MEM-42"
    assert plan.plan_network_id == "NET1"
    assert plan.group_number == "GRP1"
    assert plan.drug_formulary_number == "FORM1"
    assert plan.coverage_id == "COV1"
    assert plan.description == "Acme Premier"
    assert plan.rejected is False
    assert plan.reject_reason is None
    assert plan.service_types == ["MEDICAL", "RX"]


def test_eligibility_plan_from_dict_minimal_payload() -> None:
    """Missing optional fields default to None / empty without erroring."""
    plan = EligibilityPlan.from_dict({"pbm_name": "Acme", "payer_id": "P", "member_id": "M"})

    assert plan.pbm_name == "Acme"
    assert plan.plan_network_id is None
    assert plan.group_number is None
    assert plan.drug_formulary_number is None
    assert plan.coverage_id is None
    assert plan.description is None
    assert plan.rejected is False
    assert plan.reject_reason is None
    assert plan.service_types == []


def test_eligibility_plan_from_dict_rejected_flag_truthy() -> None:
    """Truthy non-bool rejected values coerce to True."""
    plan = EligibilityPlan.from_dict({"rejected": "yes", "reject_reason": "Coverage terminated"})

    assert plan.rejected is True
    assert plan.reject_reason == "Coverage terminated"


def test_response_from_context_happy_path() -> None:
    """A populated context parses into a SurescriptsEligibilityResponse with plans."""
    response = SurescriptsEligibilityResponse.from_context(
        {
            "correlation_id": "abc-123",
            "patient_id": "patient-key-1",
            "plans": [
                {"pbm_name": "Acme", "payer_id": "P1", "member_id": "M1"},
                {"pbm_name": "Globex", "payer_id": "P2", "member_id": "M2"},
            ],
            "error": None,
        }
    )

    assert response.correlation_id == "abc-123"
    assert response.patient_id == "patient-key-1"
    assert len(response.plans) == 2
    assert response.plans[0].pbm_name == "Acme"
    assert response.plans[1].pbm_name == "Globex"
    assert response.error is None


def test_response_from_context_error_path() -> None:
    """An error context parses with the error string and an empty plans list."""
    response = SurescriptsEligibilityResponse.from_context(
        {
            "correlation_id": "abc-123",
            "patient_id": "patient-key-1",
            "plans": [],
            "error": "Pharmacy upstream timeout",
        }
    )

    assert response.correlation_id == "abc-123"
    assert response.plans == []
    assert response.error == "Pharmacy upstream timeout"


def test_response_from_context_empty() -> None:
    """An empty context still produces a default-shaped response."""
    response = SurescriptsEligibilityResponse.from_context({})

    assert response.correlation_id == ""
    assert response.patient_id == ""
    assert response.plans == []
    assert response.error is None


def test_therapeutic_alternative_from_dict_full_payload() -> None:
    """An enriched alternative dict round-trips with per-alternative coverage detail."""
    alt = TherapeuticAlternative.from_dict(
        {
            "ndc": "00093505698",
            "description": "atorvastatin 10 mg tablet",
            "brand_or_generic": "Generic",
            "rx_or_otc": "Rx",
            "formulary_status": "On Formulary",
            "copays": ["Tier 1: $10.00"],
            "prior_authorization_required": True,
            "step_therapy_required": True,
            "quantity_limits": ["30 fills per 1 calendar year"],
        }
    )

    assert alt.ndc == "00093505698"
    assert alt.description == "atorvastatin 10 mg tablet"
    assert alt.brand_or_generic == "Generic"
    assert alt.rx_or_otc == "Rx"
    assert alt.formulary_status == "On Formulary"
    assert alt.copays == ["Tier 1: $10.00"]
    assert alt.prior_authorization_required is True
    assert alt.step_therapy_required is True
    assert alt.quantity_limits == ["30 fills per 1 calendar year"]


def test_therapeutic_alternative_from_dict_minimal_payload() -> None:
    """Missing coverage fields default to None / empty / False without erroring."""
    alt = TherapeuticAlternative.from_dict({"ndc": "00093505698"})

    assert alt.ndc == "00093505698"
    assert alt.description is None
    assert alt.brand_or_generic is None
    assert alt.rx_or_otc is None
    assert alt.formulary_status is None
    assert alt.copays == []
    assert alt.prior_authorization_required is False
    assert alt.step_therapy_required is False
    assert alt.quantity_limits == []


def test_benefit_coverage_from_dict_full_payload() -> None:
    """A fully populated coverage dict round-trips into a BenefitCoverage dataclass."""
    coverage = BenefitCoverage.from_dict(
        {
            "pbm_name": "Acme PBM",
            "payer_id": "PAYER1",
            "formulary_status": "On Formulary",
            "prior_authorization_required": True,
            "step_therapy_required": True,
            "quantity_limits": ["30 fills per 1 calendar year"],
            "copays": ["Tier 2: $25.00"],
            "alternatives": [
                {"ndc": "00093505698", "description": "atorvastatin 10 mg tablet"},
            ],
            "rejected": False,
            "reject_reason": None,
        }
    )

    assert coverage.pbm_name == "Acme PBM"
    assert coverage.payer_id == "PAYER1"
    assert coverage.formulary_status == "On Formulary"
    assert coverage.prior_authorization_required is True
    assert coverage.step_therapy_required is True
    assert coverage.quantity_limits == ["30 fills per 1 calendar year"]
    assert coverage.copays == ["Tier 2: $25.00"]
    assert len(coverage.alternatives) == 1
    assert coverage.alternatives[0].ndc == "00093505698"
    assert coverage.rejected is False
    assert coverage.reject_reason is None


def test_benefit_coverage_from_dict_minimal_payload() -> None:
    """Missing optional fields default to None / empty / False without erroring."""
    coverage = BenefitCoverage.from_dict({"pbm_name": "Acme", "payer_id": "P1"})

    assert coverage.pbm_name == "Acme"
    assert coverage.formulary_status is None
    assert coverage.prior_authorization_required is False
    assert coverage.step_therapy_required is False
    assert coverage.quantity_limits == []
    assert coverage.copays == []
    assert coverage.alternatives == []
    assert coverage.rejected is False
    assert coverage.reject_reason is None


def test_benefit_coverage_from_dict_flags_coerce_to_bool() -> None:
    """Truthy non-bool flag values coerce to True."""
    coverage = BenefitCoverage.from_dict(
        {"prior_authorization_required": "yes", "step_therapy_required": 1, "rejected": "y"}
    )

    assert coverage.prior_authorization_required is True
    assert coverage.step_therapy_required is True
    assert coverage.rejected is True


def test_benefits_response_from_context_happy_path() -> None:
    """A populated context parses into a SurescriptsBenefitsResponse with coverages."""
    response = SurescriptsBenefitsResponse.from_context(
        {
            "correlation_id": "abc-123",
            "patient_id": "patient-key-1",
            "medication_ndc": "00071015523",
            "coverages": [
                {"pbm_name": "Acme", "payer_id": "P1", "formulary_status": "On Formulary"},
                {"pbm_name": "Globex", "payer_id": "P2", "formulary_status": "Non-Formulary"},
            ],
            "error": None,
        }
    )

    assert response.correlation_id == "abc-123"
    assert response.patient_id == "patient-key-1"
    assert response.medication_ndc == "00071015523"
    assert len(response.coverages) == 2
    assert response.coverages[0].pbm_name == "Acme"
    assert response.coverages[1].formulary_status == "Non-Formulary"
    assert response.error is None


def test_benefits_response_from_context_error_path() -> None:
    """An error context parses with the error string and an empty coverages list."""
    response = SurescriptsBenefitsResponse.from_context(
        {
            "correlation_id": "abc-123",
            "patient_id": "patient-key-1",
            "medication_ndc": "00071015523",
            "coverages": [],
            "error": "pharmacy_upstream_error",
        }
    )

    assert response.correlation_id == "abc-123"
    assert response.coverages == []
    assert response.error == "pharmacy_upstream_error"


def test_benefits_response_from_context_empty() -> None:
    """An empty context still produces a default-shaped response."""
    response = SurescriptsBenefitsResponse.from_context({})

    assert response.correlation_id == ""
    assert response.patient_id == ""
    assert response.medication_ndc == ""
    assert response.coverages == []
    assert response.error is None
