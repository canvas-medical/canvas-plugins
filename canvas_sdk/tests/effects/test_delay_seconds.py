import inspect
import warnings

import pytest

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.base import _BaseEffect


class _TestEffect(_BaseEffect):
    """A minimal effect for testing delay_seconds behavior."""

    class Meta:
        effect_type = EffectType.LOG


class _FakeEffect:
    """A class whose name contains 'Effect' but is not the real ``Effect``."""


def test_delay_seconds_not_set_by_default() -> None:
    """When delay_seconds is not passed to apply(), HasField should return False."""
    effect = _TestEffect().apply()
    assert not effect.HasField("delay_seconds")


def test_delay_seconds_set_to_zero() -> None:
    """apply(delay_seconds=0) should set the field (async, no delay)."""
    effect = _TestEffect().apply(delay_seconds=0)  # type: ignore[call-arg]
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 0


def test_delay_seconds_set_to_positive() -> None:
    """apply(delay_seconds=60) should set the field with the correct value."""
    effect = _TestEffect().apply(delay_seconds=60)  # type: ignore[call-arg]
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 60


def test_delay_seconds_none_does_not_set_field() -> None:
    """Explicitly passing delay_seconds=None should not set the field."""
    effect = _TestEffect().apply(delay_seconds=None)  # type: ignore[call-arg]
    assert not effect.HasField("delay_seconds")


def test_negative_delay_seconds_raises() -> None:
    """Negative delay_seconds should raise ValueError."""
    import pytest

    with pytest.raises(ValueError, match="delay_seconds must be non-negative"):
        _TestEffect().apply(delay_seconds=-5)  # type: ignore[call-arg]


def test_non_integer_delay_seconds_raises() -> None:
    """Non-integer delay_seconds (float, bool, str) should raise ValueError."""
    with pytest.raises(ValueError, match="delay_seconds must be an integer, got float"):
        _TestEffect().apply(delay_seconds=1.5)  # type: ignore[call-arg]

    with pytest.raises(ValueError, match="delay_seconds must be an integer, got bool"):
        _TestEffect().apply(delay_seconds=True)  # type: ignore[call-arg]

    with pytest.raises(ValueError, match="delay_seconds must be an integer, got str"):
        _TestEffect().apply(delay_seconds="5")  # type: ignore[call-arg]


def test_string_annotation_to_effect_gets_wrapped() -> None:
    """A string return annotation that resolves to ``Effect`` should be auto-wrapped."""

    class _StringAnnotatedEffect(_BaseEffect):
        class Meta:
            effect_type = EffectType.LOG

        def do_thing(self) -> "Effect":
            return self.apply()

    sig = inspect.signature(_StringAnnotatedEffect.do_thing)
    assert "delay_seconds" in sig.parameters


def test_string_annotation_resolving_to_non_effect_is_not_wrapped() -> None:
    """A string annotation containing 'Effect' but resolving to another type is not wrapped."""

    class _ReturnsFakeEffect(_BaseEffect):
        class Meta:
            effect_type = EffectType.LOG

        def do_thing(self) -> "_FakeEffect":
            return _FakeEffect()

    sig = inspect.signature(_ReturnsFakeEffect.do_thing)
    assert "delay_seconds" not in sig.parameters


def test_method_with_var_keyword_is_wrapped_correctly() -> None:
    """A method with **kwargs should get delay_seconds inserted before VAR_KEYWORD."""

    class _VarKwargsEffect(_BaseEffect):
        class Meta:
            effect_type = EffectType.LOG

        def do_thing(self, name: str, **extra: object) -> Effect:
            return self.apply()

    sig = inspect.signature(_VarKwargsEffect.do_thing)
    kinds = [p.kind for p in sig.parameters.values()]
    assert "delay_seconds" in sig.parameters
    delay_idx = list(sig.parameters).index("delay_seconds")
    extra_idx = list(sig.parameters).index("extra")
    assert delay_idx < extra_idx
    assert kinds[delay_idx] == inspect.Parameter.KEYWORD_ONLY
    assert kinds[extra_idx] == inspect.Parameter.VAR_KEYWORD


def test_unresolvable_string_annotation_emits_warning() -> None:
    """An unresolvable string annotation mentioning 'Effect' should emit a warning."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")

        class _BadAnnotationEffect(_BaseEffect):
            class Meta:
                effect_type = EffectType.LOG

            def do_thing(self) -> "UndefinedEffect":  # type: ignore[name-defined]  # noqa: F821
                return self.apply()

    messages = [str(w.message) for w in caught if issubclass(w.category, UserWarning)]
    assert any("do_thing" in m and "delay_seconds" in m for m in messages), messages
