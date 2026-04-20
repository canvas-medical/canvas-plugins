import json

import pytest

from canvas_sdk.effects import EffectType, with_async
from canvas_sdk.effects.async_props import ASYNC_PROPS_KEY
from canvas_sdk.effects.base import _BaseEffect


class _TestEffect(_BaseEffect):
    """A minimal effect for testing with_async behavior."""

    class Meta:
        effect_type = EffectType.LOG


def _get_async_props(effect: object) -> dict:
    """Return the async_props dict from an effect's payload, or ``{}``."""
    payload = json.loads(effect.payload)  # type: ignore[attr-defined]
    return payload.get(ASYNC_PROPS_KEY, {})


def test_with_async_does_nothing_when_no_options_passed() -> None:
    """Calling with_async without any options leaves async_props empty."""
    effect = with_async(_TestEffect().apply())
    assert _get_async_props(effect) == {}


def test_delay_seconds_zero_is_preserved() -> None:
    """delay_seconds=0 means async-now and should be recorded."""
    effect = with_async(_TestEffect().apply(), delay_seconds=0)
    assert _get_async_props(effect) == {"delay_seconds": 0}


def test_delay_seconds_positive_is_recorded() -> None:
    """Positive delay_seconds flows into async_props."""
    effect = with_async(_TestEffect().apply(), delay_seconds=60)
    assert _get_async_props(effect) == {"delay_seconds": 60}


def test_negative_delay_seconds_raises() -> None:
    """Negative delay_seconds should raise ValueError."""
    with pytest.raises(ValueError, match="delay_seconds must be non-negative"):
        with_async(_TestEffect().apply(), delay_seconds=-5)


def test_negative_max_retries_raises() -> None:
    """Negative max_retries should raise ValueError."""
    with pytest.raises(ValueError, match="max_retries must be non-negative"):
        with_async(_TestEffect().apply(), max_retries=-1)


def test_bool_delay_seconds_raises() -> None:
    """``delay_seconds=True`` is a type-safety trap (bool is an int); reject it."""
    with pytest.raises(TypeError, match="delay_seconds must be an int"):
        with_async(_TestEffect().apply(), delay_seconds=True)


def test_bool_max_retries_raises() -> None:
    """``max_retries=True`` is a type-safety trap; reject it."""
    with pytest.raises(TypeError, match="max_retries must be an int"):
        with_async(_TestEffect().apply(), max_retries=False)


def test_non_int_delay_seconds_raises() -> None:
    """Non-int values like floats and strings are rejected."""
    with pytest.raises(TypeError, match="delay_seconds must be an int"):
        with_async(_TestEffect().apply(), delay_seconds=1.5)  # type: ignore[arg-type]


def test_all_retry_options_recorded() -> None:
    """Every retry-related option should flow through to async_props."""
    effect = with_async(
        _TestEffect().apply(),
        delay_seconds=30,
        max_retries=3,
        retry_on_exceptions=["requests.exceptions.ConnectionError"],
        retry_on_status_codes=[500, 502, 503, 504],
        retry_backoff=True,
        retry_backoff_max=600,
        retry_jitter=True,
    )
    assert _get_async_props(effect) == {
        "delay_seconds": 30,
        "max_retries": 3,
        "retry_on_exceptions": ["requests.exceptions.ConnectionError"],
        "retry_on_status_codes": [500, 502, 503, 504],
        "retry_backoff": True,
        "retry_backoff_max": 600,
        "retry_jitter": True,
    }


def test_retry_backoff_accepts_integer_base() -> None:
    """An integer retry_backoff is recorded as-is (used as the base delay)."""
    effect = with_async(_TestEffect().apply(), retry_backoff=5)
    assert _get_async_props(effect) == {"retry_backoff": 5}


def test_retry_backoff_false_is_omitted() -> None:
    """retry_backoff=False (the default) should not leak into async_props."""
    effect = with_async(_TestEffect().apply(), delay_seconds=10)
    assert "retry_backoff" not in _get_async_props(effect)


def test_retry_backoff_zero_is_omitted() -> None:
    """retry_backoff=0 is equivalent to False and should not be recorded."""
    effect = with_async(_TestEffect().apply(), retry_backoff=0)
    assert "retry_backoff" not in _get_async_props(effect)


def test_calling_twice_merges_options() -> None:
    """Repeated with_async calls should merge rather than clobber."""
    effect = with_async(_TestEffect().apply(), delay_seconds=30)
    effect = with_async(effect, max_retries=3)
    assert _get_async_props(effect) == {"delay_seconds": 30, "max_retries": 3}


def test_preserves_existing_payload_data() -> None:
    """Non-async payload data should be left alone."""
    effect = _TestEffect().apply()
    payload = json.loads(effect.payload)
    assert payload == {"data": {}}

    effect = with_async(effect, delay_seconds=10)
    payload = json.loads(effect.payload)
    assert payload["data"] == {}
    assert payload[ASYNC_PROPS_KEY] == {"delay_seconds": 10}
