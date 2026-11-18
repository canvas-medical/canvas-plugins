import json
from typing import TypeVar
from uuid import UUID

import pytest
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands import ApproveRefillCommand, DenyRefillCommand
from canvas_sdk.commands.commands.refill_response import _RefillResponseCommand
from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import Note, RefillRequest

REFILL_REQUEST_ID = UUID("6b4f1f62-8a8a-4b49-b3a4-0d1c3b2a9e10")
COMMANDS = (ApproveRefillCommand, DenyRefillCommand)
C = TypeVar("C", bound=_RefillResponseCommand)


def _on_card(command: C) -> C:
    """Set the command id after construction so it travels outside the command data."""
    command.command_uuid = "cmd-1"
    return command


@pytest.fixture
def note() -> Note:
    """A note in a patient's chart."""
    return NoteFactory.create()


@pytest.fixture
def refill_request(note: Note) -> RefillRequest:
    """A refill request for the note's patient."""
    return RefillRequest.objects.create(patient=note.patient, content={})


def _in_note(command: C, note: Note) -> C:
    """Set the note after construction so it travels outside the command data."""
    command.note_uuid = str(note.id)
    return command


@pytest.mark.parametrize(
    ("command_cls", "prefix"),
    [(ApproveRefillCommand, "APPROVE_REFILL"), (DenyRefillCommand, "DENY_REFILL")],
)
def test_effect_names_match_the_key(command_cls: type[_RefillResponseCommand], prefix: str) -> None:
    """Effect enum names derive from the key, and only originate, edit and delete exist."""
    assert command_cls.constantized_key() == prefix
    names = EffectType.DESCRIPTOR.values_by_name
    for verb in ("ORIGINATE", "EDIT", "DELETE"):
        assert f"{verb}_{prefix}_COMMAND" in names
    for verb in ("COMMIT", "SEND", "ENTER_IN_ERROR", "SIGN", "REVIEW"):
        assert f"{verb}_{prefix}_COMMAND" not in names


@pytest.mark.django_db
def test_approve_originate_carries_the_request_and_note(
    note: Note, refill_request: RefillRequest
) -> None:
    """Originating sends the refill request id and note to the pharmacist."""
    effect = _in_note(
        ApproveRefillCommand(refill_request_id=refill_request.id, note_to_pharmacist="Ok to fill"),
        note,
    ).originate()

    assert effect.type == EffectType.ORIGINATE_APPROVE_REFILL_COMMAND
    payload = json.loads(effect.payload)
    assert payload["note"] == str(note.id)
    assert payload["commit"] is False
    assert payload["data"] == {
        "refill_request_id": str(refill_request.id),
        "note_to_pharmacist": "Ok to fill",
    }


@pytest.mark.django_db
def test_deny_originate_sends_the_reason_code(note: Note, refill_request: RefillRequest) -> None:
    """A readable reason name travels as its NCPDP code."""
    effect = _in_note(
        DenyRefillCommand(
            refill_request_id=refill_request.id,
            reason_code=DenyRefillCommand.Reason.REFILL_TOO_SOON,
        ),
        note,
    ).originate()

    assert effect.type == EffectType.ORIGINATE_DENY_REFILL_COMMAND
    assert json.loads(effect.payload)["data"] == {
        "refill_request_id": str(refill_request.id),
        "reason_code": "AD",
    }


@pytest.mark.django_db
@pytest.mark.parametrize("command_cls", COMMANDS)
def test_originate_refuses_another_patients_request(
    command_cls: type[_RefillResponseCommand], note: Note
) -> None:
    """A refill request is answered only in its own patient's chart."""
    other_patients_request = RefillRequest.objects.create(
        patient=PatientFactory.create(), content={}
    )
    command = _in_note(command_cls(refill_request_id=other_patients_request.id), note)

    with pytest.raises(ValidationError, match="does not belong to this command's patient"):
        command.originate()


@pytest.mark.django_db
@pytest.mark.parametrize("command_cls", COMMANDS)
def test_originate_refuses_an_unknown_request(
    command_cls: type[_RefillResponseCommand], note: Note
) -> None:
    """A refill request id that matches nothing is refused."""
    command = _in_note(command_cls(refill_request_id=REFILL_REQUEST_ID), note)

    with pytest.raises(ValidationError, match="does not belong to this command's patient"):
        command.originate()


def test_deny_reason_codes_match_ncpdp() -> None:
    """The codes are the fourteen the Deny Refill card offers."""
    assert sorted(DenyRefillCommand.Reason) == [
        "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AJ", "AK", "AM", "AN", "AO", "AP",
    ]  # fmt: skip


def test_deny_rejects_unknown_reason_code() -> None:
    """A code outside the NCPDP set is refused before any effect is built."""
    with pytest.raises(ValidationError):
        DenyRefillCommand(refill_request_id=REFILL_REQUEST_ID, reason_code="ZZ")  # type: ignore[arg-type]


@pytest.mark.parametrize("command_cls", COMMANDS)
@pytest.mark.parametrize("refill_request_id", [None, "", "  "], ids=["none", "empty", "blank"])
def test_originate_requires_the_refill_request(
    command_cls: type[_RefillResponseCommand], refill_request_id: str | None
) -> None:
    """A response with no refill request, or a blank one, is refused."""
    with pytest.raises(ValidationError, match="refill_request_id"):
        command_cls(note_uuid="note-1", refill_request_id=refill_request_id).originate()  # type: ignore[arg-type]


@pytest.mark.parametrize("command_cls", COMMANDS)
def test_refill_request_id_must_be_a_uuid(command_cls: type[_RefillResponseCommand]) -> None:
    """A malformed id is refused when the command is built."""
    with pytest.raises(ValidationError, match="refill_request_id"):
        command_cls(refill_request_id="not-a-uuid")  # type: ignore[arg-type]


@pytest.mark.parametrize("command_cls", COMMANDS)
@pytest.mark.parametrize(
    "note",
    ["x" * 71, "café", "line one\nline two"],
    ids=["too-long", "non-ascii", "newline"],
)
def test_note_to_pharmacist_must_be_surescripts_safe(
    command_cls: type[_RefillResponseCommand], note: str
) -> None:
    """Surescripts takes at most 70 printable ASCII characters."""
    with pytest.raises(ValidationError, match="note_to_pharmacist"):
        command_cls(refill_request_id=REFILL_REQUEST_ID, note_to_pharmacist=note)


@pytest.mark.parametrize("command_cls", COMMANDS)
def test_note_to_pharmacist_at_the_limit_is_accepted(
    command_cls: type[_RefillResponseCommand],
) -> None:
    """Seventy printable characters fit."""
    command = command_cls(refill_request_id=REFILL_REQUEST_ID, note_to_pharmacist="~" * 70)

    assert command.note_to_pharmacist == "~" * 70


@pytest.mark.parametrize("command_cls", COMMANDS)
def test_originate_refuses_to_commit(command_cls: type[_RefillResponseCommand]) -> None:
    """Only the provider sends a refill response, so a plugin cannot commit it on originate."""
    command = command_cls(note_uuid="note-1", refill_request_id=REFILL_REQUEST_ID)

    with pytest.raises(ValueError, match="cannot be committed"):
        command.originate(commit=True)


@pytest.mark.parametrize("command_cls", COMMANDS)
@pytest.mark.parametrize(
    ("method", "args", "refusal"),
    [
        ("commit", (), "cannot be committed"),
        ("enter_in_error", (), "cannot be entered in error"),
        ("set_custom_html", ("<b>Approved</b>",), "cannot carry custom HTML"),
    ],
    ids=["commit", "enter_in_error", "set_custom_html"],
)
def test_effects_home_app_refuses_are_refused_here(
    command_cls: type[_RefillResponseCommand],
    method: str,
    args: tuple[str, ...],
    refusal: str,
) -> None:
    """A plugin learns when it builds the effect that only the provider sends from the card."""
    command = command_cls(command_uuid="cmd-1")

    with pytest.raises(ValueError, match=f"{refusal}: the provider sends it"):
        getattr(command, method)(*args)


@pytest.mark.parametrize("command_cls", COMMANDS)
def test_has_no_send(command_cls: type[_RefillResponseCommand]) -> None:
    """Sending to the pharmacy is not part of the plugin API."""
    assert not hasattr(command_cls, "send")


@pytest.mark.parametrize("command_cls", COMMANDS)
def test_protocol_card_recommendation_is_refused(
    command_cls: type[_RefillResponseCommand],
) -> None:
    """A protocol card inserts commands outside the plugin effect path."""
    command = command_cls(refill_request_id=REFILL_REQUEST_ID)

    card = ProtocolCard(patient_id="p", key="k", title="t")
    card.add_recommendation(title="Respond", button="Respond", commands=[command])
    with pytest.raises(ValueError, match="protocol card"):
        card.apply()


def test_edit_carries_note_and_reason() -> None:
    """An unsent card's note and reason can be changed."""
    effect = _on_card(
        DenyRefillCommand(
            note_to_pharmacist="Needs a visit",
            reason_code=DenyRefillCommand.Reason.PATIENT_NEEDS_APPOINTMENT,
        )
    ).edit()

    assert effect.type == EffectType.EDIT_DENY_REFILL_COMMAND
    assert json.loads(effect.payload) == {
        "command": "cmd-1",
        "data": {"note_to_pharmacist": "Needs a visit", "reason_code": "AM"},
    }


@pytest.mark.parametrize("command_cls", COMMANDS)
def test_edit_refuses_to_repoint_the_request(command_cls: type[_RefillResponseCommand]) -> None:
    """The card stays tied to the request it was started for."""
    command = command_cls(command_uuid="cmd-1", refill_request_id=REFILL_REQUEST_ID)

    with pytest.raises(ValueError, match="refill_request_id cannot be changed"):
        command.edit()


@pytest.mark.parametrize("command_cls", COMMANDS)
def test_delete(command_cls: type[_RefillResponseCommand]) -> None:
    """An unsent card can be deleted."""
    effect = command_cls(command_uuid="cmd-1").delete()

    assert effect.type == EffectType.Value(f"DELETE_{command_cls.constantized_key()}_COMMAND")
    assert json.loads(effect.payload) == {"command": "cmd-1"}
