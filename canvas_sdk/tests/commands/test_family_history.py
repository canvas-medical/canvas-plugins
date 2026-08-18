import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.family_history import FamilyHistoryCommand

NOTE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
MAX_LENGTH = 512


# --- note max length ------------------------------------------------------


def test_note_accepts_max_length() -> None:
    """Note accepts a value at the 512 character limit."""
    text = "a" * MAX_LENGTH

    assert FamilyHistoryCommand(note_uuid=NOTE_UUID, note=text).note == text


def test_note_rejects_above_max_length() -> None:
    """Over the limit is refused, against the field, so a caller knows what to shorten."""
    with pytest.raises(ValidationError) as caught:
        FamilyHistoryCommand(note_uuid=NOTE_UUID, note="a" * (MAX_LENGTH + 1))

    error = caught.value.errors()[0]
    assert error["loc"] == ("note",)
    assert error["type"] == "string_too_long"


def test_note_rejects_above_max_length_on_assignment() -> None:
    """The note is validated when assigned after construction."""
    command = FamilyHistoryCommand(note_uuid=NOTE_UUID)

    with pytest.raises(ValidationError):
        command.note = "a" * (MAX_LENGTH + 1)


def test_note_defaults_to_none() -> None:
    """The note is optional and defaults to None."""
    assert FamilyHistoryCommand(note_uuid=NOTE_UUID).note is None
