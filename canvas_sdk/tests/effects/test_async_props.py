import json

import pytest

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.async_effect import ASYNC_PROPS_KEY
from canvas_sdk.effects.base import _BaseEffect


class _TestEffect(_BaseEffect):
    """A minimal effect for testing set_async behavior."""

    class Meta:
        effect_type = EffectType.LOG


def _get_async_props(effect: object) -> dict:
    """Return the async_props dict from an effect's payload, or ``{}``."""
    payload = json.loads(effect.payload)  # type: ignore[attr-defined]
    return payload.get(ASYNC_PROPS_KEY, {})


def test_set_async_does_nothing_when_no_options_passed() -> None:
    """Calling set_async without any options leaves the async_props key absent."""
    effect = _TestEffect().apply().set_async()
    assert ASYNC_PROPS_KEY not in json.loads(effect.payload)


def test_set_async_returns_same_effect_for_chaining() -> None:
    """set_async should return the same effect instance so calls can chain."""
    effect = _TestEffect().apply()
    assert effect.set_async(delay_seconds=1) is effect


def test_delay_seconds_zero_is_preserved() -> None:
    """delay_seconds=0 means async-now and should be recorded."""
    effect = _TestEffect().apply().set_async(delay_seconds=0)
    assert _get_async_props(effect) == {"delay_seconds": 0}


def test_delay_seconds_positive_is_recorded() -> None:
    """Positive delay_seconds flows into async_props."""
    effect = _TestEffect().apply().set_async(delay_seconds=60)
    assert _get_async_props(effect) == {"delay_seconds": 60}


def test_negative_delay_seconds_raises() -> None:
    """Negative delay_seconds should raise ValueError."""
    with pytest.raises(ValueError, match="delay_seconds must be non-negative"):
        _TestEffect().apply().set_async(delay_seconds=-5)


def test_negative_max_retries_raises() -> None:
    """Negative max_retries should raise ValueError."""
    with pytest.raises(ValueError, match="max_retries must be non-negative"):
        _TestEffect().apply().set_async(max_retries=-1)


def test_bool_delay_seconds_raises() -> None:
    """``delay_seconds=True`` is a type-safety trap (bool is an int); reject it."""
    with pytest.raises(TypeError, match="delay_seconds must be an int"):
        _TestEffect().apply().set_async(delay_seconds=True)


def test_bool_max_retries_raises() -> None:
    """``max_retries=True`` is a type-safety trap; reject it."""
    with pytest.raises(TypeError, match="max_retries must be an int"):
        _TestEffect().apply().set_async(max_retries=True)


def test_non_int_delay_seconds_raises() -> None:
    """Non-int values like floats and strings are rejected."""
    with pytest.raises(TypeError, match="delay_seconds must be an int"):
        _TestEffect().apply().set_async(delay_seconds=1.5)  # type: ignore[arg-type]


def test_all_options_recorded() -> None:
    """Every option should flow through to async_props."""
    effect = (
        _TestEffect()
        .apply()
        .set_async(
            delay_seconds=30,
            max_retries=3,
            retry_on_status_codes=[500, 502, 503, 504],
        )
    )
    assert _get_async_props(effect) == {
        "delay_seconds": 30,
        "max_retries": 3,
        "retry_on_status_codes": [500, 502, 503, 504],
    }


def test_bare_string_retry_on_status_codes_raises() -> None:
    """A bare string would iterate char-by-char via list(); reject it."""
    with pytest.raises(TypeError, match="retry_on_status_codes must be a list of ints"):
        _TestEffect().apply().set_async(retry_on_status_codes="500,502")  # type: ignore[arg-type]


def test_non_int_retry_on_status_codes_item_raises() -> None:
    """Each retry_on_status_codes item must be an int."""
    with pytest.raises(TypeError, match="retry_on_status_codes items must be ints"):
        _TestEffect().apply().set_async(retry_on_status_codes=[500, "502"])  # type: ignore[list-item]


def test_bool_retry_on_status_codes_item_raises() -> None:
    """``True`` is an int in Python but not a valid status code; reject it."""
    with pytest.raises(TypeError, match="retry_on_status_codes items must be ints"):
        _TestEffect().apply().set_async(retry_on_status_codes=[True])


def test_out_of_range_retry_on_status_codes_raises() -> None:
    """Status codes outside 100-599 are rejected."""
    with pytest.raises(ValueError, match="valid HTTP status codes"):
        _TestEffect().apply().set_async(retry_on_status_codes=[42])
    with pytest.raises(ValueError, match="valid HTTP status codes"):
        _TestEffect().apply().set_async(retry_on_status_codes=[600])


def test_empty_payload_starts_a_fresh_async_props_dict() -> None:
    """When the effect has no payload yet, set_async should seed a new one."""
    effect = Effect()
    assert effect.payload == ""

    effect.set_async(delay_seconds=5)

    assert json.loads(effect.payload) == {ASYNC_PROPS_KEY: {"delay_seconds": 5}}


def test_non_json_payload_raises_descriptive_error() -> None:
    """A non-JSON effect payload should raise a clear ValueError, not JSONDecodeError."""
    effect = _TestEffect().apply()
    effect.payload = "Hello, world!"
    with pytest.raises(ValueError, match="Effect payload must be valid JSON to use set_async"):
        effect.set_async(delay_seconds=1)


def test_preserves_existing_payload_data() -> None:
    """Non-async payload data should be left alone."""
    effect = _TestEffect().apply()
    payload = json.loads(effect.payload)
    assert payload == {"data": {}}

    effect.set_async(delay_seconds=10)
    payload = json.loads(effect.payload)
    assert payload["data"] == {}
    assert payload[ASYNC_PROPS_KEY] == {"delay_seconds": 10}
