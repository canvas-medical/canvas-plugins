from canvas_sdk.effects import EffectType
from canvas_sdk.effects.base import _BaseEffect


class _TestEffect(_BaseEffect):
    """A minimal effect for testing delay_seconds behavior."""

    class Meta:
        effect_type = EffectType.LOG


def test_delay_seconds_not_set_by_default() -> None:
    """When delay_seconds is not provided, HasField should return False."""
    effect = _TestEffect().apply()
    assert not effect.HasField("delay_seconds")


def test_delay_seconds_set_to_zero() -> None:
    """delay_seconds=0 should set the field (async, no delay)."""
    effect = _TestEffect(delay_seconds=0).apply()
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 0


def test_delay_seconds_set_to_positive() -> None:
    """delay_seconds=60 should set the field with the correct value."""
    effect = _TestEffect(delay_seconds=60).apply()
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 60


def test_delay_seconds_none_does_not_set_field() -> None:
    """Explicitly passing delay_seconds=None should not set the field."""
    effect = _TestEffect(delay_seconds=None).apply()
    assert not effect.HasField("delay_seconds")
