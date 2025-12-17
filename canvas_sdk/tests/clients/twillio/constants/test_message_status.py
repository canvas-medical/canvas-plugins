from canvas_sdk.clients.twillio.constants.message_status import MessageStatus


def test_enum() -> None:
    """Test MessageStatus enum has correct values and member count."""
    tested = MessageStatus
    assert len(tested) == 13
    assert tested.ACCEPTED.value == "accepted"
    assert tested.SCHEDULED.value == "scheduled"
    assert tested.CANCELED.value == "canceled"
    assert tested.QUEUED.value == "queued"
    assert tested.SENDING.value == "sending"
    assert tested.SENT.value == "sent"
    assert tested.FAILED.value == "failed"
    assert tested.DELIVERED.value == "delivered"
    assert tested.UNDELIVERED.value == "undelivered"
    assert tested.PARTIALLY_DELIVERED.value == "partially_delivered"
    assert tested.RECEIVING.value == "receiving"
    assert tested.RECEIVED.value == "received"
    assert tested.READ.value == "read"
