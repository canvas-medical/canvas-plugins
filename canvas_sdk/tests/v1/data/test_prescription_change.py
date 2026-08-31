import pytest
from django.db import models

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    PrescriptionChangeRequestCodingFactory,
    PrescriptionChangeRequestFactory,
    PrescriptionChangeResponseFactory,
)
from canvas_sdk.v1.data.prescription_change import (
    PrescriptionChangeRequest,
    PrescriptionChangeRequestCoding,
    PrescriptionChangeResponse,
    PrescriptionChangeResponseStatus,
    PrescriptionChangeResponseType,
)


def test_response_type_and_status_choices() -> None:
    """The enums mirror the home-app approve/deny + status values."""
    assert PrescriptionChangeResponseType.APPROVED == "A"
    assert PrescriptionChangeResponseType.DENIED == "D"
    assert PrescriptionChangeResponseStatus.ULTIMATELY_ACCEPTED == "ultimately-accepted"
    assert PrescriptionChangeResponseStatus.ERROR == "error"


def test_fields() -> None:
    """PrescriptionChangeResponse exposes the response_type and pharmacist-note fields."""
    assert isinstance(PrescriptionChangeResponse._meta.get_field("response_type"), models.CharField)
    assert isinstance(
        PrescriptionChangeResponse._meta.get_field("note_to_pharmacist"), models.CharField
    )


def test_change_request_fields() -> None:
    """PrescriptionChangeRequest exposes the message_id and content fields."""
    assert isinstance(PrescriptionChangeRequest._meta.get_field("message_id"), models.CharField)
    assert isinstance(PrescriptionChangeRequest._meta.get_field("content"), models.JSONField)


@pytest.mark.django_db
def test_response_links_to_change_request() -> None:
    """A response resolves its originating change request via the request FK."""
    request = PrescriptionChangeRequestFactory.create(message_id="RX-1")
    response = PrescriptionChangeResponseFactory.create(request=request)

    assert response.request == request
    assert list(request.response.all()) == [response]


@pytest.mark.django_db
def test_coding_links_to_change_request() -> None:
    """A coding resolves its change request via the FK and is reachable via request.codings."""
    request = PrescriptionChangeRequestFactory.create(message_id="RX-1")
    coding = PrescriptionChangeRequestCodingFactory.create(change_request=request)

    assert coding.change_request == request
    assert list(request.codings.all()) == [coding]


def test_coding_inherits_coding_fields() -> None:
    """PrescriptionChangeRequestCoding exposes the inherited code/display/system fields."""
    for field in ("code", "display", "system"):
        assert isinstance(PrescriptionChangeRequestCoding._meta.get_field(field), models.CharField)


@pytest.mark.django_db
def test_committed_filters_and_links_to_patient() -> None:
    """committed() returns only committed, non-EIE rows, reachable via patient.prescription_change_responses."""
    committer = CanvasUserFactory.create()
    committed = PrescriptionChangeResponseFactory.create(committer=committer)
    PrescriptionChangeResponseFactory.create(committer=None)
    PrescriptionChangeResponseFactory.create(
        committer=committer, entered_in_error=CanvasUserFactory.create()
    )

    assert set(PrescriptionChangeResponse.objects.committed()) == {committed}
    assert list(committed.patient.prescription_change_responses.all()) == [committed]
