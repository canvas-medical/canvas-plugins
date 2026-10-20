from canvas_sdk.v1.data import Message, Team


def test_message_team_is_nullable_fk_to_team() -> None:
    """Message.team is a nullable foreign key to Team."""
    field = Message._meta.get_field("team")
    assert field.related_model is Team
    assert field.null is True
