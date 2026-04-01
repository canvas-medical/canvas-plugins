import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.base import _BaseCommand


class _TestCommand(_BaseCommand):
    class Meta:
        key = "testCommand"


@pytest.fixture
def mock_command_exists() -> Generator[MagicMock]:
    """Mock Command.objects to simulate an existing command."""
    with patch("canvas_sdk.effects.command_metadata.base.Command.objects") as mock_command:
        mock_command.filter.return_value.exists.return_value = True
        yield mock_command


@pytest.fixture
def mock_command_not_exists() -> Generator[MagicMock]:
    """Mock Command.objects to simulate a non-existing command."""
    with patch("canvas_sdk.effects.command_metadata.base.Command.objects") as mock_command:
        mock_command.filter.return_value.exists.return_value = False
        yield mock_command


def test_upsert_metadata_creates_effect_with_correct_type(
    mock_command_exists: MagicMock,
) -> None:
    """Test that upsert_metadata creates an Effect with the correct type."""
    cmd = _TestCommand(command_uuid="test-command-id")
    effect = cmd.upsert_metadata(key="test_key", value="test_value")

    assert effect.type == EffectType.UPSERT_COMMAND_METADATA


def test_upsert_metadata_creates_effect_with_correct_payload(
    mock_command_exists: MagicMock,
) -> None:
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


def test_upsert_metadata_validates_command_exists_with_schema_key(
    mock_command_exists: MagicMock,
) -> None:
    """Test that upsert_metadata validates command existence using both command_id and schema_key."""
    cmd = _TestCommand(command_uuid="test-command-id")
    cmd.upsert_metadata(key="test_key", value="test_value")

    mock_command_exists.filter.assert_called_once_with(
        id="test-command-id", schema_key="testCommand"
    )


def test_upsert_metadata_fails_when_command_does_not_exist(
    mock_command_not_exists: MagicMock,
) -> None:
    """Test that upsert_metadata validates the command exists."""
    cmd = _TestCommand(command_uuid="nonexistent-command-id")

    with pytest.raises(ValidationError) as exc_info:
        cmd.upsert_metadata(key="test_key", value="test_value")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "nonexistent-command-id" in errors[0]["msg"]
    assert "testCommand" in errors[0]["msg"]


def test_upsert_metadata_passes_when_command_exists(mock_command_exists: MagicMock) -> None:
    """Test that upsert_metadata succeeds when the command exists."""
    cmd = _TestCommand(command_uuid="existing-command-id")

    effect = cmd.upsert_metadata(key="test_key", value="test_value")
    assert effect is not None


def test_upsert_metadata_fails_without_command_uuid() -> None:
    """Test that upsert_metadata raises ValueError when command_uuid is not set."""
    cmd = _TestCommand(note_uuid="some-note")

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.upsert_metadata(key="test_key", value="test_value")
