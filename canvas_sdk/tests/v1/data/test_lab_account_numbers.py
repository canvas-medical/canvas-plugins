import pytest

from canvas_sdk.test_utils.factories import (
    LabPartnerFactory,
    PracticeLocationFactory,
    PracticeLocationLabAccountNumberFactory,
    StaffFactory,
    StaffLabAccountNumberFactory,
    StaffLabAccountNumberStaffFactory,
)
from canvas_sdk.v1.data import PracticeLocationLabAccountNumber, StaffLabAccountNumber


@pytest.mark.django_db
def test_location_account_number_resolves_from_location_and_lab_partner() -> None:
    """A location's lab account number is reachable from the location and from the lab partner."""
    location = PracticeLocationFactory.create()
    lab_partner = LabPartnerFactory.create()
    account = PracticeLocationLabAccountNumberFactory.create(
        practice_location=location, lab_partner=lab_partner, account_number="ACCT-1"
    )
    PracticeLocationLabAccountNumberFactory.create()

    fetched = PracticeLocationLabAccountNumber.objects.get(id=account.id)

    assert fetched.practice_location == location
    assert fetched.lab_partner == lab_partner
    assert fetched.account_number == "ACCT-1"
    assert list(location.lab_account_numbers.all()) == [account]
    assert list(lab_partner.location_account_numbers.all()) == [account]


@pytest.mark.django_db
def test_staff_account_numbers_resolve_from_location_account() -> None:
    """A location's lab account lists the staff account numbers under it."""
    location_account = PracticeLocationLabAccountNumberFactory.create()
    staff_account = StaffLabAccountNumberFactory.create(
        practice_location_lab_account=location_account, use_for_all_staff_at_location=False
    )
    StaffLabAccountNumberFactory.create()

    fetched = StaffLabAccountNumber.objects.get(id=staff_account.id)

    assert fetched.practice_location_lab_account == location_account
    assert fetched.use_for_all_staff_at_location is False
    assert list(location_account.staff_account_numbers.all()) == [staff_account]


@pytest.mark.django_db
def test_staff_account_number_staff_resolve_both_ways() -> None:
    """A staff account number lists its staff, and a staff member lists their account numbers."""
    link = StaffLabAccountNumberStaffFactory.create()
    staff_account, staff = link.staff_lab_account_number, link.staff
    StaffFactory.create()

    assert list(StaffLabAccountNumber.objects.get(id=staff_account.id).staff.all()) == [staff]
    assert list(staff.lab_account_numbers.all()) == [staff_account]
