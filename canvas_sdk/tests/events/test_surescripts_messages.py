from canvas_sdk.events.surescripts.surescripts_messages import (
    EligibilityPlan,
    SurescriptsEligibilityResponse,
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
