import json

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.schedule_callback import ScheduleCallback


def test_schedule_callback_produces_correct_effect_type() -> None:
    """ScheduleCallback.apply() should produce SCHEDULE_CALLBACK effect type."""
    effect = ScheduleCallback(key="my-key").apply(delay_seconds=60)
    assert effect.type == EffectType.SCHEDULE_CALLBACK


def test_schedule_callback_payload_contains_key_and_context() -> None:
    """The payload should contain the key and context."""
    effect = ScheduleCallback(
        key="candid-submit-abc123",
        context={"claim_id": "abc123", "queue": "QueuedForSubmission"},
    ).apply(delay_seconds=60)

    data = json.loads(effect.payload)["data"]
    assert data["key"] == "candid-submit-abc123"
    assert data["context"]["claim_id"] == "abc123"
    assert data["context"]["queue"] == "QueuedForSubmission"


def test_schedule_callback_sets_delay_seconds() -> None:
    """delay_seconds should be set on the Effect protobuf."""
    effect = ScheduleCallback(key="my-key").apply(delay_seconds=60)
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 60


def test_schedule_callback_empty_context_defaults_to_empty_dict() -> None:
    """When context is not provided, it should default to an empty dict."""
    effect = ScheduleCallback(key="my-key").apply(delay_seconds=10)
    data = json.loads(effect.payload)["data"]
    assert data["context"] == {}
