import json

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.base import _BaseCommand, _SendableCommandMixin


class SendableDummyCommand(_BaseCommand, _SendableCommandMixin):
    """A dummy command class for testing purposes."""

    class Meta:
        # this key needs to be from an existing command to have the effect type defined.
        key = "labOrder"

    int_field: int = 0


@pytest.fixture
def sendable_dummy_command_instance() -> SendableDummyCommand:
    """Fixture to return a mock instance of DummyCommand for testing."""
    cmd = SendableDummyCommand(int_field=10)
    cmd.command_uuid = "cmd-456"
    return cmd


def test_originate_successfully_returns_send_effect(
    sendable_dummy_command_instance: SendableDummyCommand,
) -> None:
    """Test that send() successfully returns the send effect."""
    effect = sendable_dummy_command_instance.send()

    assert effect is not None
    assert effect.type == EffectType.SEND_LAB_ORDER_COMMAND
    assert json.loads(effect.payload) == {
        "command": sendable_dummy_command_instance.command_uuid,
    }


def test_originate_raises_error_when_required_fields_not_set() -> None:
    """Test that send() raises an error when a required field is not set."""
    cmd = SendableDummyCommand()

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.send()
