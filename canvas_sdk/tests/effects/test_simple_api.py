from http import HTTPStatus

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.simple_api import Broadcast, Response


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


def test_response_apply_with_delay_seconds() -> None:
    """Response.apply(delay_seconds=60) should set the field on the Effect."""
    effect = Response(content=b"ok", status_code=HTTPStatus.OK).apply(delay_seconds=60)
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 60


def test_response_apply_without_delay_seconds() -> None:
    """Response.apply() without delay_seconds should not set the field."""
    effect = Response(content=b"ok", status_code=HTTPStatus.OK).apply()
    assert not effect.HasField("delay_seconds")


def test_broadcast_apply_with_delay_seconds() -> None:
    """Broadcast.apply(delay_seconds=30) should set the field on the Effect."""
    effect = Broadcast(channel="valid_channel", message={"key": "value"}).apply(delay_seconds=30)
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 30
