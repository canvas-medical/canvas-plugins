import pytest
from django.db import models

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    PrescriptionChangeResponseFactory,
)
from canvas_sdk.v1.data.prescription_change import (
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
