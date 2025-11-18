import json

import pytest

from canvas_sdk.commands.base import _BaseCommand, _ReviewableCommandMixin
from canvas_sdk.effects import EffectType


class ReviewableDummyCommand(_BaseCommand, _ReviewableCommandMixin):
    """A dummy command class for testing purposes."""

    class Meta:
        # this key needs to be from an existing command to have the review effect type defined.
        key = "prescribe"

    int_field: int = 0


@pytest.fixture
def reviewable_dummy_command_instance() -> ReviewableDummyCommand:
    """Fixture to return a mock instance of ReviewableDummyCommand for testing."""
    cmd = ReviewableDummyCommand(int_field=10)
    cmd.command_uuid = "cmd-456"
    return cmd


def test_review_successfully_returns_review_effect(
    reviewable_dummy_command_instance: ReviewableDummyCommand,
) -> None:
    """Test that review() successfully returns the review effect."""
    effect = reviewable_dummy_command_instance.review()

    assert effect is not None
    assert effect.type == EffectType.REVIEW_PRESCRIBE_COMMAND
    assert json.loads(effect.payload) == {
        "command": reviewable_dummy_command_instance.command_uuid,
    }


def test_review_raises_error_when_required_fields_not_set() -> None:
    """Test that review() raises an error when a required field is not set."""
    cmd = ReviewableDummyCommand()

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.review()
