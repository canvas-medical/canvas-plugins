from canvas_sdk.effects import EffectType
from canvas_sdk.effects.base import _BaseEffect


class _TestEffect(_BaseEffect):
    """A minimal effect for testing delay_seconds behavior."""

    class Meta:
        effect_type = EffectType.LOG


def test_delay_seconds_not_set_by_default() -> None:
    """When delay_seconds is not passed to apply(), HasField should return False."""
    effect = _TestEffect().apply()
    assert not effect.HasField("delay_seconds")


def test_delay_seconds_set_to_zero() -> None:
    """apply(delay_seconds=0) should set the field (async, no delay)."""
    effect = _TestEffect().apply(delay_seconds=0)
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 0


def test_delay_seconds_set_to_positive() -> None:
    """apply(delay_seconds=60) should set the field with the correct value."""
    effect = _TestEffect().apply(delay_seconds=60)
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 60


def test_delay_seconds_none_does_not_set_field() -> None:
    """Explicitly passing delay_seconds=None should not set the field."""
    effect = _TestEffect().apply(delay_seconds=None)
    assert not effect.HasField("delay_seconds")


def test_negative_delay_seconds_raises() -> None:
    """Negative delay_seconds should raise ValueError."""
    import pytest

    with pytest.raises(ValueError, match="delay_seconds must be non-negative"):
        _TestEffect().apply(delay_seconds=-5)
