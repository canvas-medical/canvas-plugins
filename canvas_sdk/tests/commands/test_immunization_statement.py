import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.immunization_statement import ImmunizationStatementCommand

NOTE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
MAX_LENGTH = 255


# --- comments max length --------------------------------------------------


def test_comments_accepts_max_length() -> None:
    """Comments accepts a value at the 255 character limit."""
    text = "a" * MAX_LENGTH

    assert ImmunizationStatementCommand(note_uuid=NOTE_UUID, comments=text).comments == text


def test_comments_rejects_above_max_length() -> None:
    """Over the limit is refused, against the field, so a caller knows what to shorten."""
    with pytest.raises(ValidationError) as caught:
        ImmunizationStatementCommand(note_uuid=NOTE_UUID, comments="a" * (MAX_LENGTH + 1))

    error = caught.value.errors()[0]
    assert error["loc"] == ("comments",)
    assert error["type"] == "string_too_long"


def test_comments_rejects_above_max_length_on_assignment() -> None:
    """Comments is validated when assigned after construction."""
    command = ImmunizationStatementCommand(note_uuid=NOTE_UUID)

    with pytest.raises(ValidationError):
        command.comments = "a" * (MAX_LENGTH + 1)


def test_comments_defaults_to_none() -> None:
    """Comments is optional and defaults to None."""
    assert ImmunizationStatementCommand(note_uuid=NOTE_UUID).comments is None
