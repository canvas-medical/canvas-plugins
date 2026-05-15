import json

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.base import _BaseCommand


class _TestCommand(_BaseCommand):
    class Meta:
        key = "testCommand"


def test_upsert_metadata_creates_effect_with_correct_type() -> None:
    """Test that upsert_metadata creates an Effect with the correct type."""
    cmd = _TestCommand(command_uuid="test-command-id")
    effect = cmd.upsert_metadata(key="test_key", value="test_value")

    assert effect.type == EffectType.UPSERT_COMMAND_METADATA


def test_upsert_metadata_creates_effect_with_correct_payload() -> None:
    """Test that upsert_metadata creates an Effect with the correct payload structure."""
    cmd = _TestCommand(command_uuid="test-command-id")
    effect = cmd.upsert_metadata(key="test_key", value="test_value")

    payload = json.loads(effect.payload)
    assert payload == {
        "data": {
            "command_id": "test-command-id",
            "schema_key": "testCommand",
            "key": "test_key",
            "value": "test_value",
        }
    }


def test_upsert_metadata_fails_without_command_uuid() -> None:
    """Test that upsert_metadata raises ValueError when command_uuid is not set."""
    cmd = _TestCommand(note_uuid="some-note")

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.upsert_metadata(key="test_key", value="test_value")
