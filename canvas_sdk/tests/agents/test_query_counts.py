"""The standard read tools make the same number of queries for one row as for many."""

from collections.abc import Callable
from typing import Any

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from canvas_sdk.agents import standard_tools
from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    MedicationFactory,
    MedicationStatementFactory,
    NoteFactory,
    PatientFactory,
    PracticeLocationFactory,
    PrescriptionFactory,
    StaffFactory,
)
from canvas_sdk.v1.data import Message
from canvas_sdk.v1.data.medication import MedicationCoding


def _medication(patient: Any) -> Any:
    medication = MedicationFactory.create(patient=patient)
    MedicationCoding.objects.create(
        medication=medication,
        system="http://www.fdbhealth.com/",
        version="",
        code="123456",
        display="lisinopril 10 mg tablet",
        user_selected=False,
    )
    return medication


def _message(patient: Any) -> Any:
    return Message.objects.create(
        content="Any update on my labs?",
        sender=CanvasUserFactory.create(),
        recipient=CanvasUserFactory.create(),
        note=NoteFactory.create(patient=patient),
    )


SEEDS: dict[str, Callable[[Any], Any]] = {
    "find_medications": _medication,
    "find_medication_statements": lambda patient: MedicationStatementFactory.create(
        patient=patient, committer=CanvasUserFactory.create(), medication=_medication(patient)
    ),
    "find_prescriptions": lambda patient: PrescriptionFactory.create(
        patient=patient, committer=CanvasUserFactory.create(), medication=_medication(patient)
    ),
    "find_messages": _message,
    "find_providers": lambda patient: StaffFactory.create(
        primary_practice_location=PracticeLocationFactory.create()
    ),
}


def _queries(tool: str, patient: Any) -> tuple[int, int]:
    with CaptureQueriesContext(connection) as captured:
        rows = standard_tools.execute(tool, {"limit": 100}, ctx={"patient_id": patient.id})
    return len(captured), len(rows)


@pytest.mark.django_db
@pytest.mark.parametrize("tool", sorted(SEEDS))
def test_a_read_tool_makes_as_many_queries_for_ten_rows_as_for_one(tool: str) -> None:
    """Each row's related records come with the rows, not one query per row."""
    patient = PatientFactory.create()
    SEEDS[tool](patient)
    one, rows = _queries(tool, patient)
    for _ in range(9):
        SEEDS[tool](patient)

    ten, more_rows = _queries(tool, patient)

    assert (rows, more_rows) == (1, 10)
    assert ten == one
