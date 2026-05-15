import json

import pytest

from canvas_sdk.commands.base import _BaseCommand, _DelegateCommandMixin
from canvas_sdk.effects import EffectType


class DelegatableDummyCommand(_DelegateCommandMixin, _BaseCommand):
    """A dummy command class for testing purposes."""

    class Meta:
        # this key needs to be from an existing command to have the delegate effect type defined.
        key = "refer"

    int_field: int = 0


@pytest.fixture
def delegatable_dummy_command_instance() -> DelegatableDummyCommand:
    """Fixture to return an instance of DelegatableDummyCommand with command_uuid set."""
    cmd = DelegatableDummyCommand(int_field=10)
    cmd.command_uuid = "cmd-456"
    return cmd


def test_delegate_successfully_returns_delegate_effect(
    delegatable_dummy_command_instance: DelegatableDummyCommand,
) -> None:
    """Test that delegate() successfully returns the delegate effect."""
    effect = delegatable_dummy_command_instance.delegate()

    assert effect is not None
    assert effect.type == EffectType.DELEGATE_REFER_COMMAND
    assert json.loads(effect.payload) == {
        "command": delegatable_dummy_command_instance.command_uuid,
    }


def test_delegate_raises_error_when_required_fields_not_set() -> None:
    """Test that delegate() raises an error when command_uuid is not set."""
    cmd = DelegatableDummyCommand()

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.delegate()
