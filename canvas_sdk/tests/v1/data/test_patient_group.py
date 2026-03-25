"""Tests for PatientGroup and PatientGroupMember models."""

import pytest
from django.db import IntegrityError

from canvas_sdk.test_utils.factories import (
    PatientFactory,
    PatientGroupFactory,
    PatientGroupMemberFactory,
)
from canvas_sdk.v1.data.patient_group import PatientGroupMember


@pytest.mark.django_db
def test_patient_group_str() -> None:
    """Test that PatientGroup __str__ returns the group name."""
    group = PatientGroupFactory.create(name="Diabetes Cohort")
    assert str(group) == "Diabetes Cohort"


@pytest.mark.django_db
def test_patient_group_has_uuid_id() -> None:
    """Test that PatientGroup has a UUID id field."""
    group = PatientGroupFactory.create()
    assert group.id is not None


@pytest.mark.django_db
def test_patient_group_name_is_unique() -> None:
    """Test that PatientGroup name must be unique."""
    PatientGroupFactory.create(name="Unique Group")
    with pytest.raises(IntegrityError):
        PatientGroupFactory.create(name="Unique Group")


@pytest.mark.django_db
def test_patient_group_members_relationship() -> None:
    """Test that PatientGroup.members returns associated patients through PatientGroupMember."""
    group = PatientGroupFactory.create()
    patient = PatientFactory.create()
    PatientGroupMemberFactory.create(patient_group=group, member=patient)

    assert group.members.count() == 1
    assert group.members.first() == patient


@pytest.mark.django_db
def test_patient_group_members_multiple() -> None:
    """Test that a group can have multiple members."""
    group = PatientGroupFactory.create()
    patient_a = PatientFactory.create()
    patient_b = PatientFactory.create()
    PatientGroupMemberFactory.create(patient_group=group, member=patient_a)
    PatientGroupMemberFactory.create(patient_group=group, member=patient_b)

    assert group.members.count() == 2


@pytest.mark.django_db
def test_patient_group_member_str() -> None:
    """Test that PatientGroupMember __str__ returns a readable representation."""
    group = PatientGroupFactory.create(name="Test Group")
    patient = PatientFactory.create()
    membership = PatientGroupMemberFactory.create(patient_group=group, member=patient)

    result = str(membership)
    assert "PatientGroupMember" in result
    assert str(group.id) in result
    assert str(patient.id) in result


@pytest.mark.django_db
def test_patient_group_member_has_timestamps() -> None:
    """Test that PatientGroupMember has created and modified timestamps."""
    membership = PatientGroupMemberFactory.create()
    assert membership.created is not None
    assert membership.modified is not None


@pytest.mark.django_db
def test_patient_group_member_start_date_defaults_to_now() -> None:
    """Test that PatientGroupMember.start_date is set by default."""
    membership = PatientGroupMemberFactory.create()
    assert membership.start_date is not None


@pytest.mark.django_db
def test_patient_group_member_end_date_nullable() -> None:
    """Test that PatientGroupMember.end_date is null by default."""
    membership = PatientGroupMemberFactory.create()
    assert membership.end_date is None


@pytest.mark.django_db
def test_patient_group_member_locked_default_false() -> None:
    """Test that PatientGroupMember.locked defaults to False."""
    membership = PatientGroupMemberFactory.create()
    assert membership.locked is False


@pytest.mark.django_db
def test_patient_group_member_active_default_true() -> None:
    """Test that PatientGroupMember.active defaults to True."""
    membership = PatientGroupMemberFactory.create()
    assert membership.active is True


@pytest.mark.django_db
def test_patient_group_member_cascade_delete_group() -> None:
    """Test that deleting a group cascades to its memberships."""
    group = PatientGroupFactory.create()
    PatientGroupMemberFactory.create(patient_group=group)
    PatientGroupMemberFactory.create(patient_group=group)

    group_dbid = group.dbid
    group.delete()

    assert not PatientGroupMember.objects.filter(patient_group_id=group_dbid).exists()


@pytest.mark.django_db
def test_patient_in_multiple_groups() -> None:
    """Test that a patient can belong to multiple groups."""
    patient = PatientFactory.create()
    group_a = PatientGroupFactory.create(name="Group A")
    group_b = PatientGroupFactory.create(name="Group B")
    PatientGroupMemberFactory.create(patient_group=group_a, member=patient)
    PatientGroupMemberFactory.create(patient_group=group_b, member=patient)

    assert patient.patient_groups.count() == 2
