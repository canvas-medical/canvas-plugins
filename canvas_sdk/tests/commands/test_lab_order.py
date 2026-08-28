import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.lab_order import LabOrderCommand

NOTE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
COMMAND_UUID = "1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed"
MAX_LENGTH = 128


# --- comment max length ---------------------------------------------------
#
# Checked when an effect is built rather than when the field is set, so a plugin assembling the
# comment part-way through a handler is told when the command is written instead of crashing where
# the value is assigned.


def test_comment_at_the_limit_is_accepted() -> None:
    """The boundary belongs on the allowed side."""
    text = "a" * MAX_LENGTH

    command = LabOrderCommand(note_uuid=NOTE_UUID, comment=text)

    assert command.comment == text
    assert command.originate()


def test_an_over_long_comment_can_be_set_without_raising() -> None:
    """The regression this shape exists to prevent: assignment stays quiet."""
    text = "a" * (MAX_LENGTH + 500)
    command = LabOrderCommand(note_uuid=NOTE_UUID)

    command.comment = text

    assert command.comment == text


def test_an_over_long_comment_is_refused_when_the_effect_is_built() -> None:
    """Refused at the boundary instead, so it never reaches the chart."""
    command = LabOrderCommand(note_uuid=NOTE_UUID, comment="a" * (MAX_LENGTH + 1))

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert "comment cannot be longer than 128 characters" in str(caught.value)


def test_an_over_long_comment_is_refused_on_an_edit_too() -> None:
    """An edit carries the data as well, so the same limit applies."""
    command = LabOrderCommand(command_uuid=COMMAND_UUID, comment="a" * (MAX_LENGTH + 1))

    with pytest.raises(ValidationError):
        command.edit()


def test_comment_defaults_to_none() -> None:
    """The comment is optional and defaults to None."""
    assert LabOrderCommand(note_uuid=NOTE_UUID).comment is None
