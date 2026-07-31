import pytest

from canvas_sdk.test_utils.factories import (
    PatientFactory,
    ProtocolOverrideFactory,
)
from canvas_sdk.v1.data.protocol_override import ProtocolOverride, Status


@pytest.mark.django_db
def test_active_filters_to_active_status_only() -> None:
    """active() returns only rows whose status is ACTIVE."""
    active = ProtocolOverrideFactory.create(status=Status.ACTIVE)
    ProtocolOverrideFactory.create(status=Status.INACTIVE)

    fetched = list(ProtocolOverride.objects.active())

    assert [o.id for o in fetched] == [active.id]


@pytest.mark.django_db
def test_adjustments_filters_to_is_adjustment_for_protocol_key() -> None:
    """adjustments(key) returns only is_adjustment=True rows for that protocol key."""
    target = ProtocolOverrideFactory.create(protocol_key="HCC001v1", is_adjustment=True)
    # Wrong key
    ProtocolOverrideFactory.create(protocol_key="CMS130v6", is_adjustment=True)
    # Right key, but not an adjustment
    ProtocolOverrideFactory.create(protocol_key="HCC001v1", is_adjustment=False)

    fetched = list(ProtocolOverride.objects.adjustments("HCC001v1"))

    assert [o.id for o in fetched] == [target.id]


@pytest.mark.django_db
def test_snoozes_filters_to_is_snooze_for_protocol_key() -> None:
    """snoozes(key) returns only is_snooze=True rows for that protocol key."""
    target = ProtocolOverrideFactory.create(
        protocol_key="CMS130v6", is_snooze=True, is_adjustment=False
    )
    ProtocolOverrideFactory.create(protocol_key="HCC001v1", is_snooze=True)
    ProtocolOverrideFactory.create(protocol_key="CMS130v6", is_snooze=False)

    fetched = list(ProtocolOverride.objects.snoozes("CMS130v6"))

    assert [o.id for o in fetched] == [target.id]


@pytest.mark.django_db
def test_chained_with_for_patient_active_adjustments() -> None:
    """The new methods compose with for_patient() and committed()."""
    patient = PatientFactory.create()
    wanted = ProtocolOverrideFactory.create(
        patient=patient,
        protocol_key="HCC001v1",
        is_adjustment=True,
        status=Status.ACTIVE,
    )
    # Same patient, but inactive
    ProtocolOverrideFactory.create(
        patient=patient,
        protocol_key="HCC001v1",
        is_adjustment=True,
        status=Status.INACTIVE,
    )
    # Active adjustment, wrong patient
    ProtocolOverrideFactory.create(
        protocol_key="HCC001v1",
        is_adjustment=True,
        status=Status.ACTIVE,
    )

    fetched = list(
        ProtocolOverride.objects.for_patient(patient.id)
        .committed()
        .active()
        .adjustments("HCC001v1")
    )

    assert [o.id for o in fetched] == [wanted.id]
