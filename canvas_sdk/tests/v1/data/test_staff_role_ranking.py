"""Tests for Staff.top_clinical_role privilege-level ranking."""

import pytest

from canvas_sdk.test_utils.factories.staff import StaffFactory, StaffRoleFactory
from canvas_sdk.v1.data.staff import StaffRole


@pytest.mark.django_db
def test_top_clinical_role_returns_highest_privilege_level() -> None:
    """top_clinical_role returns the clinical role with the greatest domain_privilege_level."""
    staff = StaffFactory.create()
    staff.roles.all().delete()

    # Create the lower-privilege role first so a naive "first role" impl picks the wrong one.
    StaffRoleFactory.create(
        staff=staff,
        internal_code="RN",
        name="Registered Nurse",
        public_abbreviation="RN",
        domain=StaffRole.RoleDomain.CLINICAL,
        domain_privilege_level=100,
    )
    top = StaffRoleFactory.create(
        staff=staff,
        internal_code="MD",
        name="Physician",
        public_abbreviation="MD",
        domain=StaffRole.RoleDomain.CLINICAL,
        domain_privilege_level=1000,
    )

    assert staff.top_clinical_role == top
    assert staff.top_role_abbreviation == "MD"


@pytest.mark.django_db
def test_top_clinical_role_ignores_higher_privilege_administrative_role() -> None:
    """Administrative-domain roles are excluded even at a higher privilege level."""
    staff = StaffFactory.create()
    staff.roles.all().delete()

    StaffRoleFactory.create(
        staff=staff,
        internal_code="OM",
        name="Office Manager",
        public_abbreviation="OM",
        domain=StaffRole.RoleDomain.ADMINISTRATIVE,
        domain_privilege_level=999999,
    )
    clinical = StaffRoleFactory.create(
        staff=staff,
        internal_code="RN",
        name="Registered Nurse",
        public_abbreviation="RN",
        domain=StaffRole.RoleDomain.CLINICAL,
        domain_privilege_level=100,
    )

    assert staff.top_clinical_role == clinical


@pytest.mark.django_db
def test_top_clinical_role_includes_hybrid_domain() -> None:
    """Hybrid-domain roles are eligible and rank by privilege level."""
    staff = StaffFactory.create()
    staff.roles.all().delete()

    StaffRoleFactory.create(
        staff=staff,
        internal_code="RN",
        public_abbreviation="RN",
        domain=StaffRole.RoleDomain.CLINICAL,
        domain_privilege_level=100,
    )
    top = StaffRoleFactory.create(
        staff=staff,
        internal_code="CC",
        public_abbreviation="CC",
        domain=StaffRole.RoleDomain.HYBRID,
        domain_privilege_level=500,
    )

    assert staff.top_clinical_role == top


@pytest.mark.django_db
def test_top_clinical_role_none_without_clinical_roles() -> None:
    """top_clinical_role and top_role_abbreviation are None with only non-clinical roles."""
    staff = StaffFactory.create()
    staff.roles.all().delete()

    StaffRoleFactory.create(
        staff=staff,
        internal_code="OM",
        public_abbreviation="OM",
        domain=StaffRole.RoleDomain.ADMINISTRATIVE,
        domain_privilege_level=100,
    )

    assert staff.top_clinical_role is None
    assert staff.top_role_abbreviation is None
