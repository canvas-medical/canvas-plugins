from canvas_sdk.v1.data.eligibility_response import (
    EligibilityResponse,
    EligibilityResponseStatus,
)


def _response_with_benefit_info(services: list) -> EligibilityResponse:
    response = EligibilityResponse()
    response.errors = None
    response.parsed_x12_response = {
        "receivers": [{"subscribers": [{"eligibility_or_benefit_information": services}]}]
    }
    return response


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
