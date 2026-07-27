import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    ChangeMedicationFactory,
    MedicationFactory,
)
from canvas_sdk.v1.data import ChangeMedication


@pytest.mark.django_db
def test_change_medication_exposes_sig_and_medication_relation() -> None:
    """A ChangeMedication exposes its sig and is reachable via medication.change_medications."""
    medication = MedicationFactory.create()
    change_medication = ChangeMedicationFactory.create(
        medication=medication,
        patient=medication.patient,
        sig_original_input="Take 2 tablets by mouth at bedtime",
    )

    related = list(medication.change_medications.all())

    assert related == [change_medication]
    assert related[0].sig_original_input == "Take 2 tablets by mouth at bedtime"


@pytest.mark.django_db
def test_committed_filters_uncommitted_and_entered_in_error() -> None:
    """ChangeMedication.objects.committed() returns only committed, non-EIE rows."""
    committer = CanvasUserFactory.create()

    committed = ChangeMedicationFactory.create(committer=committer)
    # Uncommitted (no committer) — excluded.
    ChangeMedicationFactory.create(committer=None)
    # Committed but entered in error — excluded.
    ChangeMedicationFactory.create(committer=committer, entered_in_error=CanvasUserFactory.create())

    assert set(ChangeMedication.objects.committed()) == {committed}
