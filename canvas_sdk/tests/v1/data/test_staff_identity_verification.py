import datetime

import pytest

from canvas_sdk.test_utils.factories import StaffFactory, StaffIdentityVerificationFactory
from canvas_sdk.v1.data import Staff, StaffIdentityVerification


@pytest.mark.django_db
def test_prescriber_verified_more_than_once_is_verified_with_latest_date() -> None:
    """A prescriber with several verifications counts as verified, latest date first."""
    staff = StaffFactory.create()
    earlier = datetime.datetime(2026, 1, 5, 12, 0, tzinfo=datetime.UTC)
    latest = datetime.datetime(2026, 10, 18, 9, 30, tzinfo=datetime.UTC)
    StaffIdentityVerificationFactory.create(staff=staff, verified_at=earlier)
    StaffIdentityVerificationFactory.create(staff=staff, verified_at=latest)

    latest_verification = staff.identity_verifications.first()

    assert latest_verification is not None
    assert latest_verification.verified_at == latest


@pytest.mark.django_db
def test_staff_who_never_verified_has_no_verifications() -> None:
    """A staff member who never verified with ID.me comes back as not verified."""
    staff = StaffFactory.create()
    StaffIdentityVerificationFactory.create()

    assert not staff.identity_verifications.exists()


@pytest.mark.django_db
def test_verified_staff_can_be_filtered_from_staff() -> None:
    """Staff with at least one verification can be selected in one query."""
    verified = StaffIdentityVerificationFactory.create().staff
    StaffIdentityVerificationFactory.create(staff=verified)
    StaffFactory.create()

    assert list(Staff.objects.filter(identity_verifications__isnull=False).distinct()) == [verified]


def test_model_omits_idme_identity_attributes_and_notes() -> None:
    """The ID.me attribute payload, ID.me UUID, and mismatch notes are not on the model."""
    field_names = {field.name for field in StaffIdentityVerification._meta.get_fields()}

    assert field_names.isdisjoint({"attributes", "idme_uuid", "notes"})
