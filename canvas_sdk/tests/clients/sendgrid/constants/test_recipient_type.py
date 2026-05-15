from canvas_sdk.clients.sendgrid.constants.recipient_type import RecipientType


def test_enum() -> None:
    """Test RecipientType enum has correct values and member count."""
    tested = RecipientType
    assert len(tested) == 3
    assert tested.TO.value == "to"
    assert tested.CC.value == "cc"
    assert tested.BCC.value == "bcc"
