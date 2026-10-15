from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.events_pb2 import EventType
from canvas_sdk.v1.data import Message, Team


def test_assign_message_team_effect_type_exists() -> None:
    """ASSIGN_MESSAGE_TEAM is a registered effect type."""
    assert EffectType.Value("ASSIGN_MESSAGE_TEAM") == 6067


def test_message_team_assigned_event_type_exists() -> None:
    """MESSAGE_TEAM_ASSIGNED is a registered event type."""
    assert EventType.Value("MESSAGE_TEAM_ASSIGNED") == 190000


def test_message_team_is_nullable_fk_to_team() -> None:
    """Message.team is a nullable foreign key to Team."""
    field = Message._meta.get_field("team")
    assert field.related_model is Team
    assert field.null is True
