import pytest
from pydantic import ValidationError

from canvas_sdk.effects.simple_api import Broadcast


def test_broadcast_effect_valid_channel() -> None:
    """Test the BroadcastEffect with a valid channel."""
    effect = Broadcast(channel="valid_channel", message={"key": "value"})
    assert effect._get_error_details("apply") == []


@pytest.mark.parametrize(
    "channel",
    [
        "!invalid_channel",
        "invalid-channel",
        "invalid channel",
        "invalid/channel",
    ],
)
def test_broadcast_effect_invalid_channel(channel: str) -> None:
    """Test the BroadcastEffect with an invalid channel."""
    with pytest.raises(ValidationError, match="Invalid channel"):
        Broadcast(channel=channel, message={"key": "value"}).apply()
