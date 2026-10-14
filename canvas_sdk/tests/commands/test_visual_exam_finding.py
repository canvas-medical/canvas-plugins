import json

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands import VisualExamFindingCommand

UPLOAD_KEY = "acme/plugin-uploads/my_plugin/20261014T120000Z-abc-rash.jpg"


def _anchored(command: VisualExamFindingCommand) -> VisualExamFindingCommand:
    """Attach note and command ids after construction so they stay out of the payload."""
    command.note_uuid = "note-123"
    command.command_uuid = "cmd-456"
    return command


def test_constantized_key_matches_the_effect_names() -> None:
    """Effect enum names derive from the key, so the two have to agree."""
    assert VisualExamFindingCommand().constantized_key() == "VISUAL_EXAM_FINDING"


def test_originate_carries_every_field() -> None:
    """Originating sends the title, narrative and image upload key."""
    effect = _anchored(
        VisualExamFindingCommand(
            title="Rash", narrative="Left forearm", image_upload_key=UPLOAD_KEY
        )
    ).originate()

    assert effect.type == EffectType.ORIGINATE_VISUAL_EXAM_FINDING_COMMAND
    assert json.loads(effect.payload)["data"] == {
        "title": "Rash",
        "narrative": "Left forearm",
        "image_upload_key": UPLOAD_KEY,
    }


def test_edit_sends_only_the_new_image() -> None:
    """Editing with only an image sends only the image key."""
    command = _anchored(VisualExamFindingCommand())
    command.image_upload_key = UPLOAD_KEY

    effect = command.edit()

    assert effect.type == EffectType.EDIT_VISUAL_EXAM_FINDING_COMMAND
    assert json.loads(effect.payload)["data"] == {"image_upload_key": UPLOAD_KEY}


@pytest.mark.parametrize("method", ["originate", "edit"])
def test_rejects_keys_outside_plugin_uploads(method: str) -> None:
    """The image key must come from a file_uploads='stored' route."""
    command = _anchored(VisualExamFindingCommand(image_upload_key="rash.jpg"))

    with pytest.raises(ValidationError, match="image_upload_key"):
        getattr(command, method)()
