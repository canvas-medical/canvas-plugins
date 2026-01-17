"""Tests for ProtocolOverride models and querysets."""

import pytest

from canvas_sdk.test_utils.factories import PatientFactory, ProtocolOverrideFactory
from canvas_sdk.v1.data.protocol_override import ProtocolOverride, Status

TESTING_PROTOCOL_KEY_1 = "CMS125v14"
TESTING_PROTOCOL_KEY_2 = "CMS130v14"


@pytest.mark.django_db
def test_get_active_adjustment_returns_matching_override() -> None:
    """Test that get_active_adjustment returns the matching active adjustment."""
    patient = PatientFactory.create()
    override = ProtocolOverrideFactory.create(
        patient=patient,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=False,
        status=Status.ACTIVE,
        is_adjustment=True,
    )

    result = ProtocolOverride.objects.get_active_adjustment(
        patient=patient, protocol_key=TESTING_PROTOCOL_KEY_1
    )

    assert result is not None
    assert result.dbid == override.dbid


@pytest.mark.django_db
def test_get_active_adjustment_returns_none_when_no_match() -> None:
    """Test that get_active_adjustment returns None when no matching override exists."""
    patient = PatientFactory.create()

    result = ProtocolOverride.objects.get_active_adjustment(
        patient=patient, protocol_key=TESTING_PROTOCOL_KEY_1
    )

    assert result is None


@pytest.mark.django_db
def test_get_active_adjustment_filters_by_patient() -> None:
    """Test that get_active_adjustment filters by patient correctly."""
    patient1 = PatientFactory.create()
    patient2 = PatientFactory.create()
    ProtocolOverrideFactory.create(
        patient=patient1,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=False,
        status=Status.ACTIVE,
        is_adjustment=True,
    )

    result = ProtocolOverride.objects.get_active_adjustment(
        patient=patient2, protocol_key=TESTING_PROTOCOL_KEY_1
    )

    assert result is None


@pytest.mark.django_db
def test_get_active_adjustment_filters_by_protocol_key() -> None:
    """Test that get_active_adjustment filters by protocol_key correctly."""
    patient = PatientFactory.create()
    ProtocolOverrideFactory.create(
        patient=patient,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=False,
        status=Status.ACTIVE,
        is_adjustment=True,
    )

    result = ProtocolOverride.objects.get_active_adjustment(
        patient=patient, protocol_key=TESTING_PROTOCOL_KEY_2
    )

    assert result is None


@pytest.mark.django_db
def test_get_active_adjustment_excludes_deleted() -> None:
    """Test that get_active_adjustment excludes deleted overrides."""
    patient = PatientFactory.create()
    ProtocolOverrideFactory.create(
        patient=patient,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=True,
        status=Status.ACTIVE,
        is_adjustment=True,
    )

    result = ProtocolOverride.objects.get_active_adjustment(
        patient=patient, protocol_key=TESTING_PROTOCOL_KEY_1
    )

    assert result is None


@pytest.mark.django_db
def test_get_active_adjustment_excludes_inactive_status() -> None:
    """Test that get_active_adjustment excludes overrides with inactive status."""
    patient = PatientFactory.create()
    ProtocolOverrideFactory.create(
        patient=patient,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=False,
        status=Status.INACTIVE,
        is_adjustment=True,
    )

    result = ProtocolOverride.objects.get_active_adjustment(
        patient=patient, protocol_key=TESTING_PROTOCOL_KEY_1
    )

    assert result is None


@pytest.mark.django_db
def test_get_active_adjustment_excludes_non_adjustments() -> None:
    """Test that get_active_adjustment excludes overrides where is_adjustment=False."""
    patient = PatientFactory.create()
    ProtocolOverrideFactory.create(
        patient=patient,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=False,
        status=Status.ACTIVE,
        is_adjustment=False,
    )

    result = ProtocolOverride.objects.get_active_adjustment(
        patient=patient, protocol_key=TESTING_PROTOCOL_KEY_1
    )

    assert result is None


@pytest.mark.django_db
def test_get_active_adjustment_finds_match_among_mixed_overrides() -> None:
    """Test that get_active_adjustment finds the correct match when multiple overrides exist.

    This verifies all filters work together correctly when the database contains
    a mix of overrides with different patients, protocols, statuses, and types.
    """
    target_patient = PatientFactory.create()
    other_patient = PatientFactory.create()

    # Create various overrides that should NOT match
    # Different patient
    ProtocolOverrideFactory.create(
        patient=other_patient,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=False,
        status=Status.ACTIVE,
        is_adjustment=True,
    )
    # Different protocol
    ProtocolOverrideFactory.create(
        patient=target_patient,
        protocol_key=TESTING_PROTOCOL_KEY_2,
        deleted=False,
        status=Status.ACTIVE,
        is_adjustment=True,
    )
    # Deleted
    ProtocolOverrideFactory.create(
        patient=target_patient,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=True,
        status=Status.ACTIVE,
        is_adjustment=True,
    )
    # Inactive
    ProtocolOverrideFactory.create(
        patient=target_patient,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=False,
        status=Status.INACTIVE,
        is_adjustment=True,
    )
    # Not an adjustment (exclusion/snooze)
    ProtocolOverrideFactory.create(
        patient=target_patient,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=False,
        status=Status.ACTIVE,
        is_adjustment=False,
    )

    # Create the ONE override that should match
    expected = ProtocolOverrideFactory.create(
        patient=target_patient,
        protocol_key=TESTING_PROTOCOL_KEY_1,
        deleted=False,
        status=Status.ACTIVE,
        is_adjustment=True,
    )

    result = ProtocolOverride.objects.get_active_adjustment(
        patient=target_patient, protocol_key=TESTING_PROTOCOL_KEY_1
    )

    assert result is not None
    assert result.dbid == expected.dbid
