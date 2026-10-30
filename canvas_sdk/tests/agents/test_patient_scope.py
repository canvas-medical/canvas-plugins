"""The standard read tools read only the run's patient's records.

Every patient-scoped read tool is run against a patient, and each query it makes on the
table its rows come from must be restricted to that patient. Removing a tool's patient
filter fails its case here even where no factory can build rows for the model.
"""

import json
import re
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol, cast
from uuid import uuid4

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from canvas_sdk.agents import standard_tools
from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    ExternalEventFactory,
    GoalFactory,
    ImagingReportFactory,
    LabReportFactory,
    LabValueFactory,
    MedicationFactory,
    MedicationStatementFactory,
    NoteFactory,
    PatientFactory,
    PrescriptionFactory,
    ProtocolCurrentFactory,
    ReferralFactory,
    StaffFactory,
    TaskFactory,
)
from canvas_sdk.v1.data.note import CurrentNoteStateEvent, Note, NoteStates

# Customer-level configuration, not any one patient's records.
UNSCOPED_CATEGORIES = {"config_reads"}


def _patient_read_tools() -> list[str]:
    return sorted(
        definition["name"]
        for definition in standard_tools.definitions()
        if standard_tools.metadata_for(definition["name"]).get("kind") == "filter_search"
        and not UNSCOPED_CATEGORIES & set(standard_tools.categories_for(definition["name"]))
    )


def _row_queries(tool: str, sql: list[str]) -> list[str]:
    table = standard_tools.metadata_for(tool)["model"]._meta.db_table
    return [query for query in sql if re.search(rf'FROM "{table}"', query)]


@pytest.mark.django_db
@pytest.mark.parametrize("tool", _patient_read_tools())
def test_each_read_tool_restricts_its_rows_to_the_runs_patient(tool: str) -> None:
    """The model cannot read another chart through any standard read tool."""
    patient = PatientFactory.create()

    with CaptureQueriesContext(connection) as queries:
        standard_tools.execute(tool, {}, ctx={"patient_id": patient.id, "effects": []})

    row_queries = _row_queries(tool, [query["sql"] for query in queries.captured_queries])
    assert row_queries, f"{tool} read nothing from its model's table"
    for query in row_queries:
        assert str(patient.id) in query or re.search(rf"\b{patient.dbid}\b", query), (
            f"{tool} read its rows without the patient: {query}"
        )


class _Record(Protocol):
    """A patient's row, which the read tools return by its ``id``."""

    @property
    def id(self) -> object: ...


def _ctx(patient_id: str, **extra: object) -> dict[str, object]:
    return {"patient_id": patient_id, "effects": [], **extra}


def _open_note(**kwargs: object) -> Note:
    """A note in NEW state; the current-state view is a plain table in tests."""
    note = NoteFactory.create(**kwargs)
    CurrentNoteStateEvent.objects.create(note=note, state=NoteStates.NEW)
    return note


@pytest.mark.django_db
@pytest.mark.parametrize(
    "tool, create",
    [
        ("find_tasks", TaskFactory.create),
        ("find_notes", NoteFactory.create),
        ("find_medications", MedicationFactory.create),
    ],
)
def test_another_patients_rows_are_absent(tool: str, create: Callable[..., _Record]) -> None:
    """With records on two charts, a read returns only the run's patient's."""
    patient, other = PatientFactory.create(), PatientFactory.create()
    own = create(patient=patient)
    create(patient=other)
    arguments = {"status": "OPEN"} if tool == "find_tasks" else {}

    result = standard_tools.execute(tool, arguments, ctx=_ctx(patient.id))

    ids = {row["id"] for row in result}
    assert ids == {str(own.id)}


@pytest.mark.django_db
def test_get_note_content_returns_nothing_for_another_patients_note() -> None:
    """A note id from another chart reads as a note that does not exist."""
    patient = PatientFactory.create()
    others_note = NoteFactory.create()

    result = standard_tools.execute(
        "get_note_content", {"note_id": str(others_note.id)}, ctx=_ctx(patient.id)
    )

    assert result is None


@pytest.mark.django_db
def test_get_open_note_returns_the_requesting_clinicians_note() -> None:
    """A colleague's newer open note on the chart is not the clinician's open note."""
    patient = PatientFactory.create()
    clinician = StaffFactory.create()
    own = _open_note(
        patient=patient, provider=clinician, datetime_of_service=datetime(2026, 1, 1, tzinfo=UTC)
    )
    _open_note(patient=patient, datetime_of_service=datetime(2026, 6, 1, tzinfo=UTC))

    result = standard_tools.execute(
        "get_open_note", {}, ctx=_ctx(patient.id, staff_id=clinician.id)
    )

    assert result is not None and result["id"] == str(own.id)


def _seed_lab_value(patient: object) -> _Record:
    report = LabReportFactory.create(patient=patient, junked=False)
    return cast(_Record, LabValueFactory.create(report=report))


SEEDED_READS: list[tuple[str, Callable[..., _Record]]] = [
    ("find_goals", lambda patient: GoalFactory.create(patient=patient)),
    ("find_imaging_reports", lambda patient: ImagingReportFactory.create(patient=patient)),
    ("find_referrals", lambda patient: ReferralFactory.create(patient=patient)),
    (
        "find_medication_statements",
        lambda patient: MedicationStatementFactory.create(patient=patient),
    ),
    ("find_external_events", lambda patient: ExternalEventFactory.create(patient=patient)),
    (
        "find_prescriptions",
        # The tool reads committed prescriptions.
        lambda patient: PrescriptionFactory.create(
            patient=patient, committer=CanvasUserFactory.create()
        ),
    ),
    ("find_lab_results", _seed_lab_value),
    ("find_protocol_cards", lambda patient: ProtocolCurrentFactory.create(patient=patient)),
]


@pytest.mark.django_db
@pytest.mark.parametrize("tool, seed", SEEDED_READS, ids=[tool for tool, _ in SEEDED_READS])
def test_a_read_tool_returns_its_patients_row_as_json(
    tool: str, seed: Callable[..., _Record]
) -> None:
    """Each tool's serializer turns a real row into what the model receives."""
    patient, other = PatientFactory.create(), PatientFactory.create()
    seed(patient)
    seed(other)

    result = standard_tools.execute(tool, {}, ctx=_ctx(patient.id))

    assert len(result) == 1
    json.dumps(result)


@pytest.mark.django_db
def test_get_note_content_reads_the_patients_note_in_document_order() -> None:
    """Text blocks come back in order; a command the body names but the note lacks is left out."""
    patient = PatientFactory.create()
    # A version 1 note, whose body is one list.
    note = NoteFactory.create(
        patient=patient,
        _body=[
            {"type": "text", "value": "Follow-up for blood pressure."},
            {"type": "text", "value": "   "},
            {"type": "command", "value": "plan", "data": {"command_uuid": str(uuid4())}},
            {"type": "text", "value": "Recheck in 3 months."},
        ],
    )

    result = standard_tools.execute(
        "get_note_content", {"note_id": str(note.id)}, ctx=_ctx(patient.id)
    )

    assert result["id"] == str(note.id)
    assert result["content"] == [
        {"type": "text", "value": "Follow-up for blood pressure."},
        {"type": "text", "value": "Recheck in 3 months."},
    ]
