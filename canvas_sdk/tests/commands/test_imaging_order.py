import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.imaging_order import ImagingOrderCommand

NOTE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
MAX_LENGTH = 1024


# --- additional details and comment max length ----------------------------


@pytest.mark.parametrize("field", ["additional_details", "comment"])
def test_accepts_max_length(field: str) -> None:
    """Both text fields accept a value at the 1024 character limit."""
    text = "a" * MAX_LENGTH

    command = ImagingOrderCommand.model_validate({"note_uuid": NOTE_UUID, field: text})

    assert getattr(command, field) == text


@pytest.mark.parametrize("field", ["additional_details", "comment"])
def test_rejects_above_max_length(field: str) -> None:
    """Over the limit is refused, against the field, so a caller knows which to shorten."""
    with pytest.raises(ValidationError) as caught:
        ImagingOrderCommand.model_validate({"note_uuid": NOTE_UUID, field: "a" * (MAX_LENGTH + 1)})

    error = caught.value.errors()[0]
    assert error["loc"] == (field,)
    assert error["type"] == "string_too_long"


@pytest.mark.parametrize("field", ["additional_details", "comment"])
def test_rejects_above_max_length_on_assignment(field: str) -> None:
    """Both fields are validated when assigned after construction."""
    command = ImagingOrderCommand(note_uuid=NOTE_UUID)

    with pytest.raises(ValidationError):
        setattr(command, field, "a" * (MAX_LENGTH + 1))


@pytest.mark.parametrize("field", ["additional_details", "comment"])
def test_defaults_to_none(field: str) -> None:
    """Both fields are optional and default to None."""
    assert getattr(ImagingOrderCommand(note_uuid=NOTE_UUID), field) is None
