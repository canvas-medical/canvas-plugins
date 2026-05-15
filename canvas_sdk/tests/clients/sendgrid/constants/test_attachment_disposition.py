from canvas_sdk.clients.sendgrid.constants.attachment_disposition import AttachmentDisposition


def test_enum() -> None:
    """Test AttachmentDisposition enum has correct values and member count."""
    tested = AttachmentDisposition
    assert len(tested) == 2
    assert tested.ATTACHMENT.value == "attachment"
    assert tested.INLINE.value == "inline"
