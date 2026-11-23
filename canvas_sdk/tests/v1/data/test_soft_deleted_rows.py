import pytest

from canvas_sdk.test_utils.factories import (
    AuthorizationFactory,
    ClaimCommentFactory,
    ClaimFactory,
    LabOrderFactory,
    LabOrderSpecimenFactory,
    PatientFactory,
    PatientKnownLocationFactory,
    SnapshotFactory,
)
from canvas_sdk.v1.data import (
    Authorization,
    ClaimComment,
    LabOrderSpecimen,
    PatientKnownLocation,
)
from canvas_sdk.v1.data.snapshot import Snapshot


@pytest.mark.django_db
def test_deleted_known_location_is_hidden() -> None:
    """A removed known location is hidden from the model and from the patient."""
    patient = PatientFactory.create()
    kept = PatientKnownLocationFactory.create(patient=patient)
    PatientKnownLocationFactory.create(patient=patient, deleted=True)

    assert list(PatientKnownLocation.objects.all()) == [kept]
    assert list(patient.known_locations.all()) == [kept]


@pytest.mark.django_db
def test_deleted_authorization_is_hidden() -> None:
    """A deleted authorization is hidden from the model and from the patient."""
    patient = PatientFactory.create()
    kept = AuthorizationFactory.create(patient=patient)
    AuthorizationFactory.create(patient=patient, deleted=True)

    assert list(Authorization.objects.all()) == [kept]
    assert list(patient.authorizations.all()) == [kept]


@pytest.mark.django_db
def test_deleted_lab_order_specimen_is_hidden() -> None:
    """A deleted specimen is hidden from the model and from its order."""
    order = LabOrderFactory.create()
    kept = LabOrderSpecimenFactory.create(order=order)
    LabOrderSpecimenFactory.create(order=order, deleted=True)

    assert list(LabOrderSpecimen.objects.all()) == [kept]
    assert list(order.specimens.all()) == [kept]


@pytest.mark.django_db
def test_deleted_claim_comment_is_hidden() -> None:
    """A deleted claim comment is hidden from the model and from its claim."""
    claim = ClaimFactory.create()
    kept = ClaimCommentFactory.create(claim=claim)
    ClaimCommentFactory.create(claim=claim, deleted=True)

    assert list(ClaimComment.objects.all()) == [kept]
    assert list(claim.comments.all()) == [kept]


@pytest.mark.django_db
def test_deleted_snapshot_is_hidden() -> None:
    """A deleted snapshot is hidden from the model."""
    kept = SnapshotFactory.create()
    SnapshotFactory.create(deleted=True)

    assert list(Snapshot.objects.all()) == [kept]
