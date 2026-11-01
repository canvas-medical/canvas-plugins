"""find_history: past surgeries, family history, outside vaccines, and in-office procedures."""

import json
from datetime import UTC, date, datetime
from typing import Any

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.agents.citations import Sources, cite
from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    FamilyHistoryCodingFactory,
    FamilyHistoryFactory,
    NoteFactory,
    PatientFactory,
    ProcedureCodingFactory,
    ProcedureFactory,
    StaffFactory,
)
from canvas_sdk.v1.data import (
    Condition,
    ConditionCoding,
    ImmunizationStatement,
    ImmunizationStatementCoding,
)


def _history(patient: Any, **arguments: Any) -> list[dict[str, Any]]:
    return standard_tools.execute("find_history", arguments, ctx={"patient_id": patient.id})


def _condition(
    patient: Any, name: str, *, surgical: bool, committed: bool = True, **fields: Any
) -> Any:
    condition = Condition.objects.create(
        patient=patient,
        deleted=False,
        onset_date=fields.pop("onset_date", date(2020, 1, 1)),
        resolution_date=date(2020, 1, 1),
        clinical_status=fields.pop("clinical_status", "resolved" if surgical else "active"),
        notes=fields.pop("notes", ""),
        surgical=surgical,
        committer=CanvasUserFactory.create() if committed else None,
    )
    ConditionCoding.objects.create(condition=condition, display=name, code="X", system="ICD-10")
    return condition


def _family(patient: Any, name: str, relation: str, committed: bool = True) -> Any:
    entry = FamilyHistoryFactory.create(
        patient=patient,
        relation_snomed_term=relation,
        narrative="Diagnosed at 52.",
        committer=CanvasUserFactory.create() if committed else None,
    )
    FamilyHistoryCodingFactory.create(family_history=entry, display=name)
    return entry


def _outside_vaccine(patient: Any, name: str, when: date, committed: bool = True) -> Any:
    statement = ImmunizationStatement.objects.create(
        patient=patient,
        note=NoteFactory.create(patient=patient),
        date=when,
        evidence="State registry",
        comment="",
        committer=CanvasUserFactory.create() if committed else None,
    )
    ImmunizationStatementCoding.objects.create(
        immunization_statement=statement, display=name, code="115", system="CVX"
    )
    return statement


def _procedure(patient: Any, name: str, committed: bool = True) -> Any:
    note = NoteFactory.create(
        patient=patient, datetime_of_service=datetime(2026, 5, 4, 9, tzinfo=UTC)
    )
    procedure = ProcedureFactory.create(
        patient=patient,
        note=note,
        provider=StaffFactory.create(first_name="Ana", last_name="Ruiz"),
        notes="No complications.",
        committer=CanvasUserFactory.create() if committed else None,
    )
    ProcedureCodingFactory.create(procedure=procedure, display=name)
    return procedure


@pytest.mark.django_db
def test_a_past_surgery_is_history_not_a_condition() -> None:
    """Canvas keeps surgeries as resolved surgical conditions; they belong to history."""
    patient = PatientFactory.create()
    surgery = _condition(
        patient, "Cholecystectomy", surgical=True, onset_date=date(2019, 3, 1), notes="Laparoscopic"
    )
    _condition(patient, "Type 2 diabetes", surgical=False)

    (entry,) = _history(patient, kind="surgical")
    conditions = standard_tools.execute(
        "find_conditions", {"active_only": False}, ctx={"patient_id": patient.id}
    )

    assert (entry["id"], entry["type"], entry["name"], entry["date"]) == (
        str(surgery.id),
        "Surgical history",
        "Cholecystectomy",
        "2019-03-01",
    )
    assert entry["comment"] == "Laparoscopic"
    # The SDK's Condition carries no note, so a surgery links to none.
    assert entry["note_dbid"] is None
    assert [condition["display"] for condition in conditions] == ["Type 2 diabetes"]


@pytest.mark.django_db
def test_family_history_names_the_relative() -> None:
    """'Any family history of colon cancer' is answered with who had it."""
    patient = PatientFactory.create()
    _family(patient, "Colon cancer", "Mother")

    (entry,) = _history(patient, kind="family")

    assert (entry["type"], entry["name"], entry["relation"], entry["comment"]) == (
        "Family history",
        "Colon cancer",
        "Mother",
        "Diagnosed at 52.",
    )


@pytest.mark.django_db
def test_a_vaccine_given_elsewhere_carries_its_date_and_source() -> None:
    """A shot reported by the patient or pulled from a registry, which find_immunizations misses."""
    patient = PatientFactory.create()
    _outside_vaccine(patient, "Tdap", date(2021, 8, 15))

    (entry,) = _history(patient, kind="immunization")

    assert (entry["type"], entry["name"], entry["date"], entry["evidence"]) == (
        "Immunization history",
        "Tdap",
        "2021-08-15",
        "State registry",
    )


@pytest.mark.django_db
def test_a_procedure_is_dated_by_its_note() -> None:
    """An in-office procedure has no date of its own; the note's date of service is when."""
    patient = PatientFactory.create()
    _procedure(patient, "Electrocardiogram")

    (entry,) = _history(patient, kind="procedure")

    assert (entry["type"], entry["name"], entry["date"], entry["status"], entry["provider"]) == (
        "Procedure",
        "Electrocardiogram",
        "2026-05-04",
        "completed",
        "Ana Ruiz",
    )


@pytest.mark.django_db
def test_every_kind_is_searched_by_default_and_filtered_by_name() -> None:
    """With no kind, all four come back; a name narrows across them."""
    patient = PatientFactory.create()
    _condition(patient, "Appendectomy", surgical=True)
    _family(patient, "Colon cancer", "Father")
    _outside_vaccine(patient, "Tdap", date(2021, 8, 15))
    _procedure(patient, "Colonoscopy")

    assert {entry["type"] for entry in _history(patient)} == {
        "Surgical history",
        "Family history",
        "Immunization history",
        "Procedure",
    }
    assert sorted(entry["name"] for entry in _history(patient, name_contains="colon")) == [
        "Colon cancer",
        "Colonoscopy",
    ]


@pytest.mark.django_db
def test_only_the_patients_committed_history_is_returned() -> None:
    """Another patient's entries, and uncommitted drafts, never appear, for any kind."""
    patient, other = PatientFactory.create(), PatientFactory.create()
    for owner, committed in ((other, True), (patient, False)):
        _condition(owner, "Appendectomy", surgical=True, committed=committed)
        _family(owner, "Colon cancer", "Father", committed=committed)
        _outside_vaccine(owner, "Tdap", date(2021, 8, 15), committed=committed)
        _procedure(owner, "Colonoscopy", committed=committed)

    assert _history(patient) == []


@pytest.mark.django_db
def test_a_cited_history_entry_is_described_from_its_row() -> None:
    """The source card names the kind and the relative, and links to the note."""
    patient = PatientFactory.create()
    entry = _family(patient, "Colon cancer", "Mother")
    rows = _history(patient)
    sources = Sources(standard_tools).add_all(
        [
            {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": "t1", "name": "find_history"}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": json.dumps(rows)}
                ],
            },
        ]
    )

    _, (citation,) = cite(f"Her mother had colon cancer [[cite:{entry.id}]].", sources)

    assert (citation.kind, citation.label, citation.detail, citation.note_dbid) == (
        "Family history",
        "Colon cancer",
        "Mother",
        entry.note.dbid,
    )
