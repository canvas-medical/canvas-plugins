"""Tests for the VisualExamFindingCommand SDK class."""

from __future__ import annotations

import json

from canvas_sdk.commands.commands.visual_exam_finding import VisualExamFindingCommand
from canvas_sdk.effects.effect import EffectType


def test_originate_emits_effect_with_payload() -> None:
    """Originate carries title/narrative + image_upload_key into the payload."""
    command = VisualExamFindingCommand(
        note_uuid="note-123",
        title="Mole on left arm",
        narrative="3mm, asymmetric, irregular border.",
        image_upload_key="local/plugin-uploads/derm_plugin/abc-photo.jpg",
    )
    effect = command.originate()
    assert effect.type == EffectType.ORIGINATE_VISUAL_EXAM_FINDING_COMMAND
    payload = json.loads(effect.payload)
    data = payload["data"]
    assert data["title"] == "Mole on left arm"
    assert data["narrative"] == "3mm, asymmetric, irregular border."
    assert data["image_upload_key"] == "local/plugin-uploads/derm_plugin/abc-photo.jpg"


def test_edit_emits_effect_with_command_uuid() -> None:
    """Edit carries command_uuid and only the dirty fields."""
    command = VisualExamFindingCommand(
        command_uuid="cmd-9",
        narrative="Updated.",
    )
    effect = command.edit()
    assert effect.type == EffectType.EDIT_VISUAL_EXAM_FINDING_COMMAND
    payload = json.loads(effect.payload)
    assert payload["command"] == "cmd-9"
    assert payload["data"].get("narrative") == "Updated."


def test_delete_commit_enter_in_error_emit_right_effects() -> None:
    """Pure-uuid effects route to the right EffectType enum."""
    command = VisualExamFindingCommand(command_uuid="cmd-9")
    assert command.delete().type == EffectType.DELETE_VISUAL_EXAM_FINDING_COMMAND
    assert command.commit().type == EffectType.COMMIT_VISUAL_EXAM_FINDING_COMMAND
    assert (
        command.enter_in_error().type
        == EffectType.ENTER_IN_ERROR_VISUAL_EXAM_FINDING_COMMAND
    )
