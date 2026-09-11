from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    ChangeMedicationFactory,
    MedicationFactory,
    MedicationStatementFactory,
    PrescriptionFactory,
)
from canvas_sdk.v1.data.medication import Medication


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
def test_latest_sig_falls_back_to_change_medication_when_prescription_note_is_null() -> None:
    """A prescription with a null note falls back to the change medication sig, not an error."""
    medication = MedicationFactory.create()
    PrescriptionFactory.create(
        medication=medication,
        committer=CanvasUserFactory.create(),
        sig_original_input="presc sig",
        note=None,
    )
    ChangeMedicationFactory.create(medication=medication, sig_original_input="change sig")

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


@pytest.mark.django_db
def test_with_latest_sig_avoids_per_medication_queries() -> None:
    """with_latest_sig() batches every source so latest_sig resolves with no extra query."""
    med_prescription = MedicationFactory.create()
    PrescriptionFactory.create(
        medication=med_prescription,
        committer=CanvasUserFactory.create(),
        sig_original_input="presc sig",
    )

    med_change = MedicationFactory.create()
    ChangeMedicationFactory.create(medication=med_change, sig_original_input="change sig")

    med_statement = MedicationFactory.create()
    MedicationStatementFactory.create(medication=med_statement, sig_original_input="statement sig")

    dbids = [med_prescription.dbid, med_change.dbid, med_statement.dbid]
    medications = list(Medication.objects.with_latest_sig().filter(dbid__in=dbids))

    with CaptureQueriesContext(connection) as ctx:
        sigs = {m.dbid: m.latest_sig for m in medications}

    assert len(ctx.captured_queries) == 0
    assert sigs[med_prescription.dbid] == "presc sig"
    assert sigs[med_change.dbid] == "change sig"
    assert sigs[med_statement.dbid] == "statement sig"


@pytest.mark.django_db
def test_with_latest_sig_prefetches_notes_for_date_comparison() -> None:
    """with_latest_sig() select_relates each note so the date-of-service comparison adds no query."""
    medication = MedicationFactory.create()
    PrescriptionFactory.create(
        medication=medication,
        committer=CanvasUserFactory.create(),
        sig_original_input="presc sig",
        note__datetime_of_service=timezone.now() - timedelta(days=1),
    )
    ChangeMedicationFactory.create(
        medication=medication,
        sig_original_input="change sig",
        note__datetime_of_service=timezone.now(),
    )

    fetched = Medication.objects.with_latest_sig().get(dbid=medication.dbid)

    with CaptureQueriesContext(connection) as ctx:
        latest_sig = fetched.latest_sig

    assert latest_sig == "change sig"
    assert len(ctx.captured_queries) == 0


@pytest.mark.django_db
def test_latest_sig_prescription_wins_when_its_note_is_later() -> None:
    """Both exist and the prescription's note is later -> its combined_sig wins."""
    medication = MedicationFactory.create()
    earlier = timezone.now() - timedelta(days=2)
    later = timezone.now()

    PrescriptionFactory.create(
        medication=medication,
        committer=CanvasUserFactory.create(),
        sig_original_input="presc sig",
        maximum_daily_dose="3 tabs",
        note__datetime_of_service=later,
    )
    ChangeMedicationFactory.create(
        medication=medication,
        sig_original_input="change sig",
        note__datetime_of_service=earlier,
    )

    assert medication.latest_sig == "presc sig. Maximum Daily Dose: 3 tabs"


def test_latest_sig_empty_when_unsaved() -> None:
    """An unsaved medication (no dbid) returns an empty string without a DB query."""
    assert Medication().latest_sig == ""
