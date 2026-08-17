import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.medication_statement import MedicationStatementCommand

NOTE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
MAX_LENGTH = 1000


# --- sig max length -------------------------------------------------------


def test_sig_accepts_max_length() -> None:
    """Sig accepts a value at the 1000 character limit."""
    text = "a" * MAX_LENGTH

    assert MedicationStatementCommand(note_uuid=NOTE_UUID, sig=text).sig == text


def test_sig_rejects_above_max_length() -> None:
    """Over the limit is refused, against the field, so a caller knows what to shorten."""
    with pytest.raises(ValidationError) as caught:
        MedicationStatementCommand(note_uuid=NOTE_UUID, sig="a" * (MAX_LENGTH + 1))

    error = caught.value.errors()[0]
    assert error["loc"] == ("sig",)
    assert error["type"] == "string_too_long"


def test_sig_rejects_above_max_length_on_assignment() -> None:
    """The sig is validated when assigned after construction."""
    command = MedicationStatementCommand(note_uuid=NOTE_UUID)

    with pytest.raises(ValidationError):
        command.sig = "a" * (MAX_LENGTH + 1)


def test_sig_defaults_to_none() -> None:
    """The sig is optional and defaults to None."""
    assert MedicationStatementCommand(note_uuid=NOTE_UUID).sig is None
