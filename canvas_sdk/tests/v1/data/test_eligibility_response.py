from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from canvas_sdk.v1.data.coverage import Coverage, Transactor
from canvas_sdk.v1.data.eligibility_response import (
    EligibilityResponse,
    EligibilityResponseStatus,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def _response_with_benefit_info(services: list) -> EligibilityResponse:
    response = EligibilityResponse()
    response.errors = None
    response.parsed_x12_response = {
        "receivers": [{"subscribers": [{"eligibility_or_benefit_information": services}]}]
    }
    return response


def _patient(
    birth_date: str = "1990-01-01", last_name: str = "Smith", first_name: str = "John"
) -> SimpleNamespace:
    return SimpleNamespace(birth_date=birth_date, last_name=last_name, first_name=first_name)


def _parsed_person(
    birth_date: str = "1990-01-01",
    last_name: str = "Smith",
    first_name: str = "John",
    **extra: Any,
) -> dict[str, Any]:
    person: dict[str, Any] = {
        "personal_information": {
            "last_name": last_name,
            "first_name": first_name,
            "demographic_information": {"birth_date": birth_date},
        }
    }
    person.update(extra)
    return person


def test_status_failed_when_errors_present() -> None:
    """Any errors on the response mean the check failed."""
    response = EligibilityResponse()
    response.errors = ["270/271 rejected by payer"]

    assert response.status == EligibilityResponseStatus.FAILED


def test_status_active_when_no_inactive_section() -> None:
    """An eligible section with active coverage resolves to ACTIVE."""
    response = _response_with_benefit_info(
        [
            {
                "service_type": "Health Benefit Plan Coverage",
                "info": [{"information_type": "Active Coverage"}],
            }
        ]
    )

    assert response.status == EligibilityResponseStatus.ACTIVE


def test_status_inactive_when_eligible_section_inactive() -> None:
    """An eligible section reported inactive resolves to INACTIVE."""
    response = _response_with_benefit_info(
        [
            {
                "service_type": "Health Benefit Plan Coverage",
                "info": [{"information_type": "Inactive"}],
            }
        ]
    )

    assert response.status == EligibilityResponseStatus.INACTIVE


def test_status_active_with_no_benefit_information() -> None:
    """No parseable benefit information (and no errors) is treated as ACTIVE."""
    response = EligibilityResponse()
    response.errors = None
    response.parsed_x12_response = {}

    assert response.status == EligibilityResponseStatus.ACTIVE


def test_normalize_name_strips_accents_case_and_spaces() -> None:
    """Names are unicode-normalized, lowercased, and stripped of spaces."""
    assert EligibilityResponse._normalize_name("  Renée  Múñoz ") == "reneemunoz"


def test_normalize_name_handles_none() -> None:
    """A missing name normalizes to an empty string."""
    assert EligibilityResponse._normalize_name(None) == ""


def test_is_patient_match_true_for_identical_person() -> None:
    """Matching birth date, last name, and first name is a match."""
    response = EligibilityResponse()

    assert response._is_patient_match(_parsed_person(), _patient()) is True


def test_is_patient_match_true_when_first_name_is_a_prefix() -> None:
    """A response first name that is a prefix of the patient's still matches."""
    response = EligibilityResponse()

    assert (
        response._is_patient_match(
            _parsed_person(first_name="Jon"), _patient(first_name="Jonathan")
        )
        is True
    )


def test_is_patient_match_false_on_last_name_mismatch() -> None:
    """A differing last name is not a match."""
    response = EligibilityResponse()

    assert response._is_patient_match(_parsed_person(last_name="Jones"), _patient()) is False


def test_is_patient_match_false_on_first_name_mismatch() -> None:
    """Two unrelated first names are not a match."""
    response = EligibilityResponse()

    assert (
        response._is_patient_match(_parsed_person(first_name="Alice"), _patient(first_name="Bob"))
        is False
    )


def test_is_patient_match_false_on_malformed_person() -> None:
    """A person payload missing personal_information is not a match."""
    response = EligibilityResponse()

    assert response._is_patient_match({}, _patient()) is False


def test_eligibility_info_uses_matched_subscriber(mocker: "MockerFixture") -> None:
    """When the coverage patient is the subscriber, that subscriber's benefit info is used."""
    response = EligibilityResponse()
    patient = _patient()
    mocker.patch.object(
        EligibilityResponse, "coverage", SimpleNamespace(patient=patient, subscriber=patient)
    )
    subscriber = _parsed_person(
        eligibility_or_benefit_information=[{"service_type": "Health Benefit Plan Coverage"}],
        dependents=[],
    )
    response.parsed_x12_response = {"receivers": [{"subscribers": [subscriber]}]}

    assert response.eligibility_or_benefit_information == [
        {"service_type": "Health Benefit Plan Coverage"}
    ]


def test_eligibility_info_matches_dependent(mocker: "MockerFixture") -> None:
    """When the patient is a dependent of the subscriber, the dependent's benefit info is used."""
    response = EligibilityResponse()
    patient = _patient(birth_date="2015-06-01", last_name="Smith", first_name="Kiddo")
    mocker.patch.object(
        EligibilityResponse, "coverage", SimpleNamespace(patient=patient, subscriber=object())
    )
    dependent = _parsed_person(
        birth_date="2015-06-01",
        last_name="Smith",
        first_name="Kiddo",
        eligibility_or_benefit_information=[{"service_type": "child"}],
    )
    subscriber = _parsed_person(first_name="Parent", dependents=[dependent])
    response.parsed_x12_response = {"receivers": [{"subscribers": [subscriber]}]}

    assert response.eligibility_or_benefit_information == [{"service_type": "child"}]


def test_eligibility_info_falls_back_when_subscriber_is_patient_but_mismatch(
    mocker: "MockerFixture",
) -> None:
    """Patient is the subscriber but demographics differ, so the subscriber info is used."""
    response = EligibilityResponse()
    patient = _patient()
    mocker.patch.object(
        EligibilityResponse, "coverage", SimpleNamespace(patient=patient, subscriber=patient)
    )
    subscriber = _parsed_person(
        last_name="DifferentName",
        eligibility_or_benefit_information=[{"service_type": "subscriber"}],
    )
    response.parsed_x12_response = {"receivers": [{"subscribers": [subscriber]}]}

    assert response.eligibility_or_benefit_information == [{"service_type": "subscriber"}]


def test_eligibility_info_falls_back_to_subscriber_when_no_dependent_matches(
    mocker: "MockerFixture",
) -> None:
    """No matching dependent falls back to the subscriber's own benefit info."""
    response = EligibilityResponse()
    patient = _patient(first_name="Nomatch")
    mocker.patch.object(
        EligibilityResponse, "coverage", SimpleNamespace(patient=patient, subscriber=object())
    )
    subscriber = _parsed_person(
        first_name="Parent",
        eligibility_or_benefit_information=[{"service_type": "subscriber"}],
        dependents=[
            _parsed_person(birth_date="2000-01-01", last_name="Else", first_name="Someone")
        ],
    )
    response.parsed_x12_response = {"receivers": [{"subscribers": [subscriber]}]}

    assert response.eligibility_or_benefit_information == [{"service_type": "subscriber"}]


def test_eligibility_info_handles_subscriber_without_dependents(mocker: "MockerFixture") -> None:
    """A subscriber payload lacking a dependents list falls back to its own benefit info."""
    response = EligibilityResponse()
    mocker.patch.object(
        EligibilityResponse,
        "coverage",
        SimpleNamespace(patient=_patient(), subscriber=object()),
    )
    subscriber = _parsed_person(eligibility_or_benefit_information=[{"service_type": "sub"}])
    response.parsed_x12_response = {"receivers": [{"subscribers": [subscriber]}]}

    assert response.eligibility_or_benefit_information == [{"service_type": "sub"}]


def test_eligibility_info_empty_when_no_subscribers(mocker: "MockerFixture") -> None:
    """No subscribers in the parsed response yields no benefit information."""
    response = EligibilityResponse()
    mocker.patch.object(
        EligibilityResponse,
        "coverage",
        SimpleNamespace(patient=_patient(), subscriber=object()),
    )
    response.parsed_x12_response = {"receivers": [{"subscribers": []}]}

    assert response.eligibility_or_benefit_information == []


def test_eligibility_info_empty_when_subscriber_lacks_benefit_key() -> None:
    """A subscriber payload without a benefit-information key yields an empty list."""
    response = EligibilityResponse()
    response.parsed_x12_response = {"receivers": [{"subscribers": [{"personal_information": {}}]}]}

    assert response.eligibility_or_benefit_information == []


def test_eligibility_info_empty_when_matched_person_lacks_benefit_key(
    mocker: "MockerFixture",
) -> None:
    """A matched person without a benefit-information key yields an empty list."""
    response = EligibilityResponse()
    patient = _patient()
    mocker.patch.object(
        EligibilityResponse, "coverage", SimpleNamespace(patient=patient, subscriber=patient)
    )
    response.parsed_x12_response = {"receivers": [{"subscribers": [_parsed_person()]}]}

    assert response.eligibility_or_benefit_information == []


class _FakeEligibilityResponses:
    """Stand-in for the ``eligibility_responses`` reverse manager."""

    def __init__(self, latest: Any) -> None:
        self._latest = latest
        self.order_by_args: tuple = ()

    def order_by(self, *fields: str) -> "_FakeEligibilityResponses":
        self.order_by_args = fields
        return self

    def first(self) -> Any:
        return self._latest


def test_coverage_eligibility_status_unknown_when_no_responses(mocker: "MockerFixture") -> None:
    """A coverage with no eligibility responses reports UNKNOWN (not verified)."""
    responses = _FakeEligibilityResponses(None)
    mocker.patch.object(Coverage, "eligibility_responses", responses)

    assert Coverage().eligibility_status == EligibilityResponseStatus.UNKNOWN
    assert responses.order_by_args == ("-created",)


def test_coverage_eligibility_status_uses_latest_response(mocker: "MockerFixture") -> None:
    """A coverage defers to the status of its most recent eligibility response."""
    latest = SimpleNamespace(status=EligibilityResponseStatus.INACTIVE)
    responses = _FakeEligibilityResponses(latest)
    mocker.patch.object(Coverage, "eligibility_responses", responses)

    assert Coverage().eligibility_status == EligibilityResponseStatus.INACTIVE
    assert responses.order_by_args == ("-created",)


def test_status_enum_includes_not_applicable() -> None:
    """The SDK enum carries NOT_APPLICABLE so self-pay coverages have a value to report (KOALA-6940)."""
    assert EligibilityResponseStatus.NOT_APPLICABLE.value == "NotApplicable"


def test_transactor_supports_eligibility_check() -> None:
    """A self-pay transactor (payer_id PATIENT) does not support real-time eligibility."""
    assert Transactor(payer_id="PATIENT").supports_eligibility_check is False
    assert Transactor(payer_id="AETNA").supports_eligibility_check is True


def test_self_pay_coverage_reports_not_applicable_over_stale_failed(
    mocker: "MockerFixture",
) -> None:
    """A self-pay coverage reports NOT_APPLICABLE even when it carries a stale Failed response."""
    responses = _FakeEligibilityResponses(SimpleNamespace(status=EligibilityResponseStatus.FAILED))
    mocker.patch.object(Coverage, "eligibility_responses", responses)

    coverage = Coverage()
    coverage.issuer = Transactor(payer_id="PATIENT")

    assert coverage.eligibility_status == EligibilityResponseStatus.NOT_APPLICABLE


def test_ordinary_payer_coverage_defers_to_last_response(mocker: "MockerFixture") -> None:
    """A coverage with an ordinary payer still defers to its most recent response's status."""
    responses = _FakeEligibilityResponses(SimpleNamespace(status=EligibilityResponseStatus.ACTIVE))
    mocker.patch.object(Coverage, "eligibility_responses", responses)

    coverage = Coverage()
    coverage.issuer = Transactor(payer_id="AETNA")

    assert coverage.eligibility_status == EligibilityResponseStatus.ACTIVE
