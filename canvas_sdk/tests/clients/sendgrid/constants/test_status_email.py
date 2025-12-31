from canvas_sdk.clients.sendgrid.constants.status_email import StatusEmail


def test_enum() -> None:
    """Test StatusEmail enum has correct values and member count."""
    tested = StatusEmail
    assert len(tested) == 7
    assert tested.PROCESSED.value == "processed"
    assert tested.DELIVERED.value == "delivered"
    assert tested.NOT_DELIVERED.value == "not_delivered"
    assert tested.DEFERRED.value == "deferred"
    assert tested.DROPPED.value == "dropped"
    assert tested.BOUNCED.value == "bounced"
    assert tested.BLOCKED.value == "blocked"
