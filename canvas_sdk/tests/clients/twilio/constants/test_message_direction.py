from canvas_sdk.clients.twilio.constants.message_direction import MessageDirection


def test_enum() -> None:
    """Test MessageDirection enum has correct values and member count."""
    tested = MessageDirection
    assert len(tested) == 4
    assert tested.INBOUND.value == "inbound"
    assert tested.OUTBOUND_API.value == "outbound-api"
    assert tested.OUTBOUND_CALL.value == "outbound-call"
    assert tested.OUTBOUND_REPLY.value == "outbound-reply"
