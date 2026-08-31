import pytest
from django.db import models

from canvas_sdk.test_utils.factories import CancelPrescriptionFactory, CanvasUserFactory
from canvas_sdk.v1.data.cancel_prescription import CancelPrescription, CancelPrescriptionStatus


def test_cancel_prescription_status_choices() -> None:
    """CancelPrescriptionStatus mirrors the home-app open/pending/ultimately-accepted values."""
    assert CancelPrescriptionStatus.OPEN == "open"
    assert CancelPrescriptionStatus.PENDING == "pending"
    assert CancelPrescriptionStatus.ULTIMATELY_ACCEPTED == "ultimately-accepted"


def test_cancel_prescription_fields() -> None:
    """CancelPrescription exposes the message_id and status fields."""
    assert isinstance(CancelPrescription._meta.get_field("message_id"), models.CharField)
    assert isinstance(CancelPrescription._meta.get_field("status"), models.CharField)


@pytest.mark.django_db
def test_committed_filters_and_links_to_patient() -> None:
    """committed() returns only committed, non-EIE rows, reachable via patient.cancel_prescriptions."""
    committer = CanvasUserFactory.create()
    committed = CancelPrescriptionFactory.create(committer=committer)
    CancelPrescriptionFactory.create(committer=None)
    CancelPrescriptionFactory.create(
        committer=committer, entered_in_error=CanvasUserFactory.create()
    )

    assert set(CancelPrescription.objects.committed()) == {committed}
    assert list(committed.patient.cancel_prescriptions.all()) == [committed]
