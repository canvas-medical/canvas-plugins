from canvas_sdk.clients.sendgrid.constants.event_email import EventEmail


def test_enum() -> None:
    """Test EventEmail enum has correct values and member count."""
    tested = EventEmail
    assert len(tested) == 13
    assert tested.BOUNCE.value == "bounce"
    assert tested.CLICK.value == "click"
    assert tested.DEFERRED.value == "deferred"
    assert tested.DELIVERED.value == "delivered"
    assert tested.DROPPED.value == "dropped"
    assert tested.CANCEL_DROP.value == "cancel_drop"
    assert tested.OPEN.value == "open"
    assert tested.PROCESSED.value == "processed"
    assert tested.RECEIVED.value == "received"
    assert tested.SPAM_REPORT.value == "spamreport"
    assert tested.GROUP_UNSUBSCRIBE.value == "group_unsubscribe"
    assert tested.GROUP_RESUBSCRIBE.value == "group_resubscribe"
    assert tested.UNSUBSCRIBE.value == "unsubscribe"
