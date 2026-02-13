import pytest
from pydantic import ValidationError

from canvas_sdk.effects.simple_api import Broadcast


@pytest.mark.parametrize(
    "channel",
    [
        "valid_channel",
        "valid-channel",
        "550e8400-e29b-41d4-a716-446655440000",
    ],
)
def test_broadcast_effect_valid_channel(channel: str) -> None:
    """Test the BroadcastEffect with a valid channel."""
    effect = Broadcast(channel=channel, message={"key": "value"})
    assert effect._get_error_details("apply") == []


@pytest.mark.parametrize(
    "channel",
    [
        "!invalid_channel",
        "invalid channel",
        "invalid/channel",
    ],
)
def test_broadcast_effect_invalid_channel(channel: str) -> None:
    """Test the BroadcastEffect with an invalid channel."""
    with pytest.raises(ValidationError, match="Invalid channel"):
        Broadcast(channel=channel, message={"key": "value"}).apply()
