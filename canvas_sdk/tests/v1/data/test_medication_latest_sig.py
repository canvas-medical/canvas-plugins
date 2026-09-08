from datetime import timedelta

import pytest
from django.utils import timezone

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    ChangeMedicationFactory,
    MedicationFactory,
    MedicationStatementFactory,
    PrescriptionFactory,
)


@pytest.mark.django_db
def test_latest_sig_empty_when_no_sources() -> None:
    """No prescriptions/change meds/statements -> empty string."""
    medication = MedicationFactory.create()

    assert medication.latest_sig == ""


@pytest.mark.django_db
def test_latest_sig_prescription_uses_combined_sig() -> None:
    """A lone active prescription returns combined_sig, appending the maximum daily dose."""
    medication = MedicationFactory.create()
    PrescriptionFactory.create(
        medication=medication,
        committer=CanvasUserFactory.create(),
        sig_original_input="1 tab bid",
        maximum_daily_dose="2 tabs",
    )

    assert medication.latest_sig == "1 tab bid. Maximum Daily Dose: 2 tabs"


@pytest.mark.django_db
def test_latest_sig_change_medication_when_no_prescription() -> None:
    """A lone change medication returns its sig."""
    medication = MedicationFactory.create()
    ChangeMedicationFactory.create(medication=medication, sig_original_input="2 tabs qhs")

    assert medication.latest_sig == "2 tabs qhs"


@pytest.mark.django_db
def test_latest_sig_medication_statement_when_no_others() -> None:
    """A lone medication statement returns its sig."""
    medication = MedicationFactory.create()
    MedicationStatementFactory.create(medication=medication, sig_original_input="1 tab qd")

    assert medication.latest_sig == "1 tab qd"


@pytest.mark.django_db
def test_latest_sig_prescription_and_change_medication_compare_note_date() -> None:
    """When both exist, the source whose note has the later date of service wins."""
    medication = MedicationFactory.create()
    earlier = timezone.now() - timedelta(days=2)
    later = timezone.now()

    PrescriptionFactory.create(
        medication=medication,
        committer=CanvasUserFactory.create(),
        sig_original_input="presc sig",
        note__datetime_of_service=earlier,
    )
    ChangeMedicationFactory.create(
        medication=medication,
        sig_original_input="change sig",
        note__datetime_of_service=later,
    )

    assert medication.latest_sig == "change sig"


@pytest.mark.django_db
def test_latest_sig_excludes_entered_in_error_but_keeps_status_error() -> None:
    """Entered-in-error prescriptions are excluded; status=error prescriptions are kept."""
    medication = MedicationFactory.create()
    PrescriptionFactory.create(
        medication=medication,
        committer=CanvasUserFactory.create(),
        entered_in_error=CanvasUserFactory.create(),
        sig_original_input="entered in error sig",
    )
    PrescriptionFactory.create(
        medication=medication,
        committer=CanvasUserFactory.create(),
        status="error",
        sig_original_input="status error sig",
    )

    assert medication.latest_sig == "status error sig"
