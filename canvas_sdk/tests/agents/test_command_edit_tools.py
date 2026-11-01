"""The draft edit tools: change or delete a staged draft in the run's note, and nothing else."""

import json
from typing import Any
from uuid import UUID

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.agents import standard_tools
from canvas_sdk.agents.command_edit_tools import DRAFT_KINDS
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import Command, Note, Patient

NOTE = "00000000-0000-0000-0000-000000000001"


def staged_command(
    patient: Patient,
    schema_key: str = "medicationStatement",
    *,
    note: Note | None = None,
    state: str = "staged",
) -> Command:
    """A command of ``schema_key`` on ``note``, by default a new note with id :data:`NOTE`."""
    if note is None:
        note = NoteFactory.create(patient=patient, id=UUID(NOTE))
    return Command.objects.create(
        note=note,
        patient=patient,
        schema_key=schema_key,
        data={},
        state=state,
        origination_source="ui",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


def _run(tool: str, patient: Patient, **arguments: Any) -> tuple[Any, list[Any]]:
    effects: list[Any] = []
    result = standard_tools.execute(
        tool, arguments, ctx={"patient_id": patient.id, "note_id": NOTE, "effects": effects}
    )
    return result, effects


def _sent(effect: Any) -> tuple[str, dict[str, Any]]:
    """The effect's type and payload, less the ``command_uuid`` every edit's data repeats."""
    payload = json.loads(effect.payload)
    payload.get("data", {}).pop("command_uuid", None)
    return EffectType.Name(effect.type), payload


def test_only_fields_no_check_guards_are_editable() -> None:
    """A code or a chart id an originate tool checks is never editable."""
    assert set(DRAFT_KINDS["medicationStatement"][1]) == {"sig"}
    assert "fdb_code" not in DRAFT_KINDS["prescribe"][1]
    assert set(DRAFT_KINDS["resolveCondition"][1]) == {"rationale", "show_in_condition_list"}
    assert "concept_id" not in DRAFT_KINDS["allergy"][1]


@pytest.mark.django_db
def test_an_edit_sends_only_the_changed_fields() -> None:
    """The edit names the draft and carries just what the model changed."""
    patient = PatientFactory.create()
    command = staged_command(patient)

    result, (effect,) = _run(
        "edit_staged_command", patient, command_id=str(command.id), fields={"sig": "2 daily"}
    )

    assert result == {
        "ok": True,
        "command_id": str(command.id),
        "command": "medicationStatement",
        "changed": ["sig"],
        "committed": False,
    }
    assert _sent(effect) == (
        "EDIT_MEDICATION_STATEMENT_COMMAND",
        {"command": str(command.id), "data": {"sig": "2 daily"}},
    )


@pytest.mark.django_db
def test_an_edit_maps_argument_names_onto_command_fields() -> None:
    """Fields are named as the originate tool names them, and checked as it declares them."""
    patient = PatientFactory.create()
    command = staged_command(patient, "allergy")

    _, (effect,) = _run(
        "edit_staged_command", patient, command_id=str(command.id), fields={"severity": "mild"}
    )

    assert _sent(effect)[1]["data"] == {"severity": "mild"}
    with pytest.raises(ValueError, match="severity must be one of"):
        _run("edit_staged_command", patient, command_id=str(command.id), fields={"severity": "x"})


@pytest.mark.django_db
def test_an_edit_cannot_change_what_the_originate_tool_checks() -> None:
    """Swapping the medication would skip the duplicate and controlled-substance checks."""
    patient = PatientFactory.create()
    command = staged_command(patient)

    with pytest.raises(ValueError, match="can change only sig, not fdb_code"):
        _run(
            "edit_staged_command",
            patient,
            command_id=str(command.id),
            fields={"fdb_code": "123456"},
        )


@pytest.mark.django_db
def test_a_delete_names_the_draft() -> None:
    """A staged draft in the run's note is deleted by its id."""
    patient = PatientFactory.create()
    command = staged_command(patient, "plan")

    result, (effect,) = _run("delete_staged_command", patient, command_id=str(command.id))

    assert result["ok"] is True and result["command"] == "plan"
    assert _sent(effect) == ("DELETE_PLAN_COMMAND", {"command": str(command.id)})


@pytest.mark.parametrize(
    ("setup", "message"),
    [
        (lambda patient: staged_command(patient, state="committed"), "this one is committed"),
        (lambda patient: staged_command(PatientFactory.create()), "No command with that id"),
        (
            lambda patient: staged_command(patient, note=NoteFactory.create(patient=patient)),
            "No command with that id",
        ),
        (lambda patient: staged_command(patient, "hpi"), "not one these tools change"),
    ],
    ids=["committed", "another patient", "another note", "a kind no tool stages"],
)
@pytest.mark.parametrize("tool", ["edit_staged_command", "delete_staged_command"])
@pytest.mark.django_db
def test_only_a_staged_draft_of_the_run_is_touched(tool: str, setup: Any, message: str) -> None:
    """A colleague's committed work, another chart, or another note is refused."""
    patient = PatientFactory.create()
    command = setup(patient)
    arguments: dict[str, Any] = {"command_id": str(command.id)}
    if tool == "edit_staged_command":
        arguments["fields"] = {"narrative": "x"}

    with pytest.raises(ValueError, match=message):
        _run(tool, patient, **arguments)


@pytest.mark.django_db
def test_a_draft_this_run_staged_is_deleted_before_it_reaches_the_note() -> None:
    """Deleting the run's own draft drops its originate effect; editing it is refused."""
    patient = PatientFactory.create()
    effects: list[Any] = []
    ctx = {"patient_id": patient.id, "note_id": NOTE, "effects": effects}
    staged = standard_tools.execute("originate_plan", {"narrative": "Recheck"}, ctx=ctx)

    with pytest.raises(ValueError, match="This run staged that draft"):
        standard_tools.execute(
            "edit_staged_command",
            {"command_id": staged["command_id"], "fields": {"narrative": "Later"}},
            ctx=ctx,
        )
    result = standard_tools.execute(
        "delete_staged_command", {"command_id": staged["command_id"]}, ctx=ctx
    )

    assert result["deleted"] is True
    assert effects == []
