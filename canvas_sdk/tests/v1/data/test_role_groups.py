import pytest

from canvas_sdk.test_utils.factories import (
    AuthGroupFactory,
    RoleFactory,
    RoleGroupFactory,
    RoleGroupGroupFactory,
    StaffFactory,
    StaffRoleFactory,
)
from canvas_sdk.v1.data import AuthGroup, Role, RoleGroup, StaffRole


@pytest.mark.django_db
def test_role_group_resolves_from_role() -> None:
    """A role lists its role groups, and a role group points at its role."""
    role = RoleFactory.create(internal_code="MD", name="Physician")
    role_group = RoleGroupFactory.create(role=role)
    RoleGroupFactory.create()

    fetched = RoleGroup.objects.get(id=role_group.id)

    assert fetched.role == role
    assert list(Role.objects.get(id=role.id).role_groups.all()) == [role_group]
    assert Role.objects.filter(role_groups__id=role_group.id).get().name == "Physician"


@pytest.mark.django_db
def test_role_group_groups_resolve_both_ways() -> None:
    """A role group lists its auth groups, and an auth group lists its role groups."""
    link = RoleGroupGroupFactory.create(group__name="Providers")
    role_group, group = link.role_group, link.group
    AuthGroupFactory.create()

    assert list(RoleGroup.objects.get(id=role_group.id).groups.all()) == [group]
    assert list(AuthGroup.objects.get(dbid=group.dbid).role_groups.all()) == [role_group]
    assert list(role_group.role.role_groups.filter(groups__name="Providers")) == [role_group]


@pytest.mark.django_db
def test_role_reads_its_domain_and_role_type() -> None:
    """A role keeps its domain and role type."""
    role = RoleFactory.create(domain="ADM", role_type="NON-LICENSED")

    fetched = Role.objects.get(id=role.id)

    assert (fetched.domain, fetched.role_type) == ("ADM", "NON-LICENSED")
    assert fetched.get_domain_display() == "Administrative"
    assert fetched.get_role_type_display() == "Non-Licensed"


def test_role_choices() -> None:
    """Role domains and role types are offered by stored value."""
    assert [value for value, _ in Role._meta.get_field("domain").flatchoices] == [
        "CLI",
        "ADM",
        "HYB",
    ]
    assert [value for value, _ in Role._meta.get_field("role_type").flatchoices] == [
        "NON-LICENSED",
        "LICENSED",
        "PROVIDER",
    ]


@pytest.mark.django_db
def test_staff_role_resolves_its_role() -> None:
    """A staff role points at its role, and a role lists the staff roles that hold it."""
    role = RoleFactory.create(internal_code="RN", name="Nurse")
    staff_role = StaffRoleFactory.create(
        staff=StaffFactory.create(), internal_code="RN", name="Nurse"
    )
    StaffRoleFactory.create(staff=StaffFactory.create(), internal_code="PA")

    fetched = StaffRole.objects.get(dbid=staff_role.dbid)

    assert fetched.role == role
    assert fetched.role.id == role.id
    assert list(Role.objects.get(id=role.id).staff_roles.all()) == [staff_role]
