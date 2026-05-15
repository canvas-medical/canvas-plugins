import json

import pytest

from canvas_sdk.commands.base import _BaseCommand, _SignCommandMixin
from canvas_sdk.effects import EffectType


class SignableDummyCommand(_SignCommandMixin, _BaseCommand):
    """A dummy command class for testing purposes."""

    class Meta:
        # this key needs to be from an existing command to have the sign effect type defined.
        key = "refer"

    int_field: int = 0


@pytest.fixture
def signable_dummy_command_instance() -> SignableDummyCommand:
    """Fixture to return an instance of SignableDummyCommand with command_uuid set."""
    cmd = SignableDummyCommand(int_field=10)
    cmd.command_uuid = "cmd-456"
    return cmd


def test_sign_successfully_returns_sign_effect(
    signable_dummy_command_instance: SignableDummyCommand,
) -> None:
    """Test that sign() successfully returns the sign effect."""
    effect = signable_dummy_command_instance.sign()

    assert effect is not None
    assert effect.type == EffectType.SIGN_REFER_COMMAND
    assert json.loads(effect.payload) == {
        "command": signable_dummy_command_instance.command_uuid,
    }


def test_sign_raises_error_when_required_fields_not_set() -> None:
    """Test that sign() raises an error when command_uuid is not set."""
    cmd = SignableDummyCommand()

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.sign()
