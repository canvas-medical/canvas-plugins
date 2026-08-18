import json

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.commands.allergy import AllergyCommand

NOTE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
COMMAND_UUID = "1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed"


# --- narrative max length -------------------------------------------------


def test_narrative_accepts_max_length() -> None:
    """Narrative accepts a value at the 512 character limit."""
    assert AllergyCommand(note_uuid=NOTE_UUID, narrative="a" * 512).narrative == "a" * 512


def test_narrative_rejects_above_max_length() -> None:
    """Narrative rejects a value over the 512 character limit, against the field."""
    with pytest.raises(ValidationError) as caught:
        AllergyCommand(note_uuid=NOTE_UUID, narrative="a" * 513)

    error = caught.value.errors()[0]
    assert error["loc"] == ("narrative",)
    assert error["type"] == "string_too_long"


def test_narrative_rejects_above_max_length_on_assignment() -> None:
    """Narrative is validated when assigned after construction."""
    allergy = AllergyCommand(note_uuid=NOTE_UUID)

    with pytest.raises(ValidationError):
        allergy.narrative = "a" * 513


@pytest.mark.parametrize("narrative", [None, ""])
def test_narrative_is_optional(narrative: str | None) -> None:
    """An allergy can be recorded without describing the reaction."""
    assert AllergyCommand(note_uuid=NOTE_UUID, narrative=narrative).narrative == narrative


def test_narrative_defaults_to_none() -> None:
    """Narrative defaults to None."""
    assert AllergyCommand(note_uuid=NOTE_UUID).narrative is None


def test_narrative_reaches_the_originate_payload() -> None:
    """The limit guards a value that is actually sent, not one dropped on the way out."""
    command = AllergyCommand(
        note_uuid=NOTE_UUID, command_uuid=COMMAND_UUID, narrative="Hives within an hour"
    )

    effect = command.originate()

    assert effect.type == EffectType.ORIGINATE_ALLERGY_COMMAND
    assert json.loads(effect.payload)["data"]["narrative"] == "Hives within an hour"
