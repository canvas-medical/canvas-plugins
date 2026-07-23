import json
from unittest.mock import patch
from uuid import uuid4

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.commands.prescribe import PrescribeCommand


def test_send_without_override_omits_key() -> None:
    """send() with no override produces the unchanged command-only payload."""
    cmd = PrescribeCommand(command_uuid="cmd-456")

    effect = cmd.send()

    assert effect.type == EffectType.SEND_PRESCRIBE_COMMAND
    assert json.loads(effect.payload) == {"command": "cmd-456"}


def test_send_with_override_includes_key() -> None:
    """send() with a valid override adds practice_location_override to the payload."""
    location_id = str(uuid4())
    cmd = PrescribeCommand(command_uuid="cmd-456")

    with patch("canvas_sdk.v1.data.PracticeLocation.objects") as mock_pl:
        mock_pl.filter.return_value.exists.return_value = True
        effect = cmd.send(practice_location_override=location_id)

    payload = json.loads(effect.payload)
    assert payload["command"] == "cmd-456"
    assert payload["practice_location_override"] == location_id


def test_send_with_invalid_override_raises() -> None:
    """A nonexistent override id raises ValueError before an effect is produced."""
    cmd = PrescribeCommand(command_uuid="cmd-456")

    with patch("canvas_sdk.v1.data.PracticeLocation.objects") as mock_pl:
        mock_pl.filter.return_value.exists.return_value = False
        with pytest.raises(ValueError, match="does not exist"):
            cmd.send(practice_location_override=str(uuid4()))
