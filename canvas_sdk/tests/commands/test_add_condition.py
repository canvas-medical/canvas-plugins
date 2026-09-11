import datetime
import json

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands import AddConditionCommand


def _anchored(command: AddConditionCommand) -> AddConditionCommand:
    """Attach the note and command ids after construction.

    Constructor keys are all marked dirty, while assignment honors the excluded
    list, so setting the anchors here keeps them out of the effect payload.
    """
    command.note_uuid = "note-123"
    command.command_uuid = "cmd-456"
    return command


@pytest.fixture
def command() -> AddConditionCommand:
    """A populated AddCondition command anchored to a note."""
    return _anchored(
        AddConditionCommand(
            icd10_code="N183",
            background="Diagnosed at outside nephrology practice.",
            approximate_date_of_onset=datetime.date(2023, 4, 1),
            comments="Stable on last three panels.",
        )
    )


def test_constantized_key_matches_the_effect_names() -> None:
    """The effect enum names are derived from the key, so the two have to agree."""
    assert AddConditionCommand().constantized_key() == "ADD_CONDITION"


def test_originate_carries_every_field(command: AddConditionCommand) -> None:
    """Originating sends the four fields, with the onset date as an ISO string."""
    effect = command.originate()

    assert effect.type == EffectType.ORIGINATE_ADD_CONDITION_COMMAND
    assert json.loads(effect.payload)["data"] == {
        "icd10_code": "N183",
        "background": "Diagnosed at outside nephrology practice.",
        "approximate_date_of_onset": "2023-04-01",
        "comments": "Stable on last three panels.",
    }


def test_originate_needs_no_values() -> None:
    """An empty command can be dropped into a note and filled in by hand."""
    effect = _anchored(AddConditionCommand()).originate()

    assert effect.type == EffectType.ORIGINATE_ADD_CONDITION_COMMAND
    assert json.loads(effect.payload)["data"] == {}


def test_only_the_fields_that_were_set_are_sent() -> None:
    """Dirty tracking keeps an untouched field out of the payload."""
    effect = _anchored(AddConditionCommand(icd10_code="N183")).originate()

    assert json.loads(effect.payload)["data"] == {"icd10_code": "N183"}


def test_commit_needs_only_the_command_id() -> None:
    """A command staged in the note is committed by id, without restating its fields."""
    command = AddConditionCommand()
    command.command_uuid = "cmd-456"

    assert command.commit().type == EffectType.COMMIT_ADD_CONDITION_COMMAND


def test_commit_returns_the_commit_effect(command: AddConditionCommand) -> None:
    """A command carrying a code commits."""
    assert command.commit().type == EffectType.COMMIT_ADD_CONDITION_COMMAND


def test_edit_returns_the_edit_effect(command: AddConditionCommand) -> None:
    """Editing targets the existing command rather than the note."""
    assert command.edit().type == EffectType.EDIT_ADD_CONDITION_COMMAND


def test_delete_returns_the_delete_effect(command: AddConditionCommand) -> None:
    """Deleting targets the existing command."""
    assert command.delete().type == EffectType.DELETE_ADD_CONDITION_COMMAND


def test_enter_in_error_returns_the_enter_in_error_effect(command: AddConditionCommand) -> None:
    """Entering in error targets the existing command."""
    assert command.enter_in_error().type == EffectType.ENTER_IN_ERROR_ADD_CONDITION_COMMAND


def test_comments_are_capped_at_the_column_length() -> None:
    """Comments are stored in a 1000 character column, so a longer value is refused."""
    with pytest.raises(ValidationError, match="comments"):
        AddConditionCommand(comments="x" * 1001)


def test_comments_at_the_limit_are_accepted() -> None:
    """A value that exactly fills the column is fine."""
    command = AddConditionCommand(comments="x" * 1000)

    assert command.comments == "x" * 1000
