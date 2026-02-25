import pytest

from canvas_sdk.test_utils.factories import CanvasUserFactory, PrescriptionFactory
from canvas_sdk.v1.data.prescription import Prescription, PrescriptionResponse


@pytest.mark.django_db
def test_active_returns_committed_non_denied_prescriptions() -> None:
    """Test that Prescription.objects.active() returns only committed, non-denied prescriptions."""
    committer = CanvasUserFactory.create()

    # Committed prescription with no response_type — should be included
    committed = PrescriptionFactory.create(committer=committer)

    # Committed prescription with APPROVED response — should be included
    committed_approved = PrescriptionFactory.create(
        committer=committer, response_type=PrescriptionResponse.APPROVED
    )

    # Committed prescription with DENIED response — should be excluded
    PrescriptionFactory.create(committer=committer, response_type=PrescriptionResponse.DENIED)

    # Uncommitted prescription (no committer) — should be excluded
    PrescriptionFactory.create(committer=None)

    # Committed but entered_in_error — should be excluded
    PrescriptionFactory.create(committer=committer, entered_in_error=CanvasUserFactory.create())

    active = Prescription.objects.active()

    assert set(active) == {committed, committed_approved}
