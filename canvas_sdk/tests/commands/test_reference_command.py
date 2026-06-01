"""Unit tests for the Reference SDK command."""

import json

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands import ReferenceCommand


def test_meta_key() -> None:
    """The command's Meta.key matches the home-app SDK schema key."""
    assert ReferenceCommand.Meta.key == "reference"


def test_originate_returns_originate_effect() -> None:
    """originate() builds an ORIGINATE_REFERENCE_COMMAND effect with the right payload."""
    cmd = ReferenceCommand(diagnostic_view_id="dca3a3c5-0a8e-4f7b-9c6a-1b9bf3a6e5e0")
    cmd.note_uuid = "note-1"
    cmd.command_uuid = "cmd-1"

    effect = cmd.originate()

    assert effect.type == EffectType.ORIGINATE_REFERENCE_COMMAND
    payload = json.loads(effect.payload)
    assert payload == {
        "command": "cmd-1",
        "note": "note-1",
        "data": {"diagnostic_view_id": "dca3a3c5-0a8e-4f7b-9c6a-1b9bf3a6e5e0"},
        "line_number": -1,
        "commit": False,
    }


def test_originate_renames_field_via_commands_api_name() -> None:
    """The command's JSON schema renames diagnostic_view_id to diagnostic_view on the wire."""
    schema = ReferenceCommand.model_json_schema()
    assert schema["properties"]["diagnostic_view_id"].get("commands_api_name") == "diagnostic_view"


def test_edit_emits_edit_effect() -> None:
    """edit() builds an EDIT_REFERENCE_COMMAND effect with the data payload."""
    cmd = ReferenceCommand(diagnostic_view_id="11111111-2222-3333-4444-555555555555")
    cmd.command_uuid = "cmd-2"

    effect = cmd.edit()

    assert effect.type == EffectType.EDIT_REFERENCE_COMMAND
    payload = json.loads(effect.payload)
    assert payload == {
        "command": "cmd-2",
        "data": {"diagnostic_view_id": "11111111-2222-3333-4444-555555555555"},
    }


def test_delete_emits_delete_effect() -> None:
    """delete() builds a DELETE_REFERENCE_COMMAND effect."""
    cmd = ReferenceCommand()
    cmd.command_uuid = "cmd-3"

    effect = cmd.delete()

    assert effect.type == EffectType.DELETE_REFERENCE_COMMAND
    assert json.loads(effect.payload) == {"command": "cmd-3"}


def test_commit_emits_commit_effect() -> None:
    """commit() builds a COMMIT_REFERENCE_COMMAND effect."""
    cmd = ReferenceCommand()
    cmd.command_uuid = "cmd-4"

    effect = cmd.commit()

    assert effect.type == EffectType.COMMIT_REFERENCE_COMMAND
    assert json.loads(effect.payload) == {"command": "cmd-4"}


def test_enter_in_error_emits_enter_in_error_effect() -> None:
    """enter_in_error() builds an ENTER_IN_ERROR_REFERENCE_COMMAND effect."""
    cmd = ReferenceCommand()
    cmd.command_uuid = "cmd-5"

    effect = cmd.enter_in_error()

    assert effect.type == EffectType.ENTER_IN_ERROR_REFERENCE_COMMAND
    assert json.loads(effect.payload) == {"command": "cmd-5"}


def test_diagnostic_view_id_is_optional() -> None:
    """diagnostic_view_id is not required at construction time."""
    cmd = ReferenceCommand()
    cmd.note_uuid = "note-1"
    cmd.command_uuid = "cmd-6"

    effect = cmd.originate()

    assert effect.type == EffectType.ORIGINATE_REFERENCE_COMMAND
    payload = json.loads(effect.payload)
    # No diagnostic_view_id was set, so it shouldn't be in the data values.
    assert payload["data"] == {}
