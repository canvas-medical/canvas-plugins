import pytest
from django.db import models

from canvas_sdk.test_utils.factories import CancelPrescriptionResponseFactory
from canvas_sdk.v1.data.cancel_prescription_response import CancelPrescriptionResponse


def test_cancel_prescription_response_fields() -> None:
    """CancelPrescriptionResponse exposes the message_id, note, reason_code, and response fields."""
    assert isinstance(CancelPrescriptionResponse._meta.get_field("message_id"), models.CharField)
    assert isinstance(CancelPrescriptionResponse._meta.get_field("note"), models.CharField)
    assert isinstance(CancelPrescriptionResponse._meta.get_field("reason_code"), models.CharField)
    assert isinstance(CancelPrescriptionResponse._meta.get_field("response"), models.CharField)


@pytest.mark.django_db
def test_links_to_patient_and_request() -> None:
    """A response is reachable via patient.cancel_prescription_responses and request.response."""
    response = CancelPrescriptionResponseFactory.create(response="approved", reason_code="AA")

    assert response.patient is not None
    assert response.request is not None
    assert list(response.patient.cancel_prescription_responses.all()) == [response]
    assert response.request.response == response
