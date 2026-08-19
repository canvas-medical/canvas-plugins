import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.update_diagnosis import UpdateDiagnosisCommand

NOTE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
COMMAND_UUID = "1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed"
MAX_LENGTH = 2048


# --- background and narrative max length ----------------------------------
#
# Checked when an effect is built rather than when the field is set. On the field it raised at the
# assigning line, which breaks a plugin assembling this text part-way through a handler. Deferring
# keeps the over-long value off the chart without crashing the handler that produced it.


@pytest.mark.parametrize("field", ["background", "narrative"])
def test_accepts_max_length(field: str) -> None:
    """The boundary belongs on the allowed side, and the value is not rewritten."""
    text = "a" * MAX_LENGTH

    command = UpdateDiagnosisCommand(note_uuid=NOTE_UUID, **{field: text})

    assert getattr(command, field) == text
    assert command.originate()


@pytest.mark.parametrize("field", ["background", "narrative"])
def test_over_long_text_can_be_set_without_raising(field: str) -> None:
    """The regression this shape exists to prevent: assignment stays quiet."""
    text = "a" * (MAX_LENGTH + 500)
    command = UpdateDiagnosisCommand(note_uuid=NOTE_UUID)

    setattr(command, field, text)

    assert getattr(command, field) == text


@pytest.mark.parametrize("field", ["background", "narrative"])
def test_over_long_text_is_refused_when_the_effect_is_built(field: str) -> None:
    """Refused at the boundary instead, so it never reaches the chart."""
    command = UpdateDiagnosisCommand(note_uuid=NOTE_UUID, **{field: "a" * (MAX_LENGTH + 1)})

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert f"{field} cannot be longer than {MAX_LENGTH} characters" in str(caught.value)


@pytest.mark.parametrize("field", ["background", "narrative"])
def test_over_long_text_is_refused_on_an_edit_too(field: str) -> None:
    """An edit carries the data as well, so the same limit applies."""
    command = UpdateDiagnosisCommand(command_uuid=COMMAND_UUID, **{field: "a" * (MAX_LENGTH + 1)})

    with pytest.raises(ValidationError):
        command.edit()


def test_both_fields_are_reported_together() -> None:
    """Deferring to the effect means a caller is told about every value at once."""
    command = UpdateDiagnosisCommand(
        note_uuid=NOTE_UUID,
        background="a" * (MAX_LENGTH + 1),
        narrative="a" * (MAX_LENGTH + 1),
    )

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert len(caught.value.errors()) == 2


@pytest.mark.parametrize("field", ["background", "narrative"])
def test_defaults_to_none(field: str) -> None:
    """Both fields are optional and default to None."""
    assert getattr(UpdateDiagnosisCommand(note_uuid=NOTE_UUID), field) is None
