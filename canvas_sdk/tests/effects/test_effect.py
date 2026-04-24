"""Tests for the SDK Effect wrapper class."""

import json

import pytest

from canvas_generated.messages.effects_pb2 import Effect as _PbEffect
from canvas_sdk.effects import Effect, EffectType, _BaseEffect
from canvas_sdk.effects.effect import ASYNC_PROPS_KEY


class _TestEffect(_BaseEffect):
    """A minimal effect for exercising the wrapper via ``.apply()``."""

    class Meta:
        effect_type = EffectType.LOG


def _get_async_props(effect: Effect) -> dict:
    """Return the async_props dict from an effect's payload, or ``{}``."""
    return json.loads(effect.payload).get(ASYNC_PROPS_KEY, {})


# --- field delegation & constructor -----------------------------------------


def test_effect_defaults_to_empty_payload_and_unknown_type() -> None:
    """A bare ``Effect()`` has empty payload and UNKNOWN_EFFECT type."""
    effect = Effect()
    assert effect.payload == ""
    assert effect.type == EffectType.UNKNOWN_EFFECT


def test_effect_constructor_sets_type_and_payload() -> None:
    """The constructor forwards ``type`` and ``payload`` to the underlying pb."""
    effect = Effect(type=EffectType.LOG, payload='{"hello": "world"}')
    assert effect.type == EffectType.LOG
    assert effect.payload == '{"hello": "world"}'


def test_effect_fields_are_mutable() -> None:
    """``type`` and ``payload`` can be reassigned after construction."""
    effect = Effect()
    effect.type = EffectType.LOG
    effect.payload = "abc"
    assert effect.type == EffectType.LOG
    assert effect.payload == "abc"


def test_base_effect_apply_returns_wrapper() -> None:
    """``_BaseEffect.apply()`` returns our wrapper, not the raw protobuf."""
    effect = _TestEffect().apply()
    assert isinstance(effect, Effect)


def test_runtime_metadata_fields_delegate_to_protobuf() -> None:
    """Protobuf-only fields like ``plugin_name`` pass through ``__getattr__``/``__setattr__``."""
    effect = Effect()
    effect.plugin_name = "my_plugin"
    effect.handler_name = "MyHandler.compute"
    assert effect.plugin_name == "my_plugin"
    assert effect.to_proto().plugin_name == "my_plugin"
    assert effect.to_proto().handler_name == "MyHandler.compute"


# --- to_proto ---------------------------------------------------------------


def test_to_proto_returns_protobuf_effect_with_same_fields() -> None:
    """``to_proto`` returns the underlying protobuf Effect with the same fields."""
    effect = Effect(type=EffectType.LOG, payload="{}")
    pb = effect.to_proto()
    assert isinstance(pb, _PbEffect)
    assert pb.type == EffectType.LOG
    assert pb.payload == "{}"


def test_to_proto_reflects_later_mutations() -> None:
    """``to_proto`` returns the same underlying pb, so later edits are visible."""
    effect = Effect(type=EffectType.LOG, payload="{}")
    pb = effect.to_proto()
    effect.payload = "mutated"
    assert pb.payload == "mutated"


# --- equality ---------------------------------------------------------------


def test_wrapper_equality_uses_underlying_pb() -> None:
    """Two wrappers are equal when their underlying pb Effects are equal."""
    a = Effect(type=EffectType.LOG, payload="{}")
    b = Effect(type=EffectType.LOG, payload="{}")
    assert a == b


def test_wrapper_equal_to_raw_protobuf_with_same_fields() -> None:
    """A wrapper compares equal to a raw protobuf with the same fields."""
    effect = Effect(type=EffectType.LOG, payload="{}")
    pb = _PbEffect(type=EffectType.LOG, payload="{}")
    assert effect == pb


# --- set_async --------------------------------------------------------------


def test_set_async_does_nothing_when_no_options_passed() -> None:
    """Calling set_async without options leaves the async_props key absent."""
    effect = _TestEffect().apply().set_async()
    assert ASYNC_PROPS_KEY not in json.loads(effect.payload)


def test_set_async_returns_same_effect_for_chaining() -> None:
    """set_async returns the same instance so calls can chain."""
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
    """Non-int values (e.g. float) are rejected."""
    with pytest.raises(TypeError, match="delay_seconds must be an int"):
        _TestEffect().apply().set_async(delay_seconds=1.5)  # type: ignore[arg-type]


def test_all_options_recorded() -> None:
    """Every option should flow through to async_props."""
    effect = _TestEffect().apply().set_async(delay_seconds=30, max_retries=3)
    assert _get_async_props(effect) == {"delay_seconds": 30, "max_retries": 3}


def test_empty_payload_starts_a_fresh_async_props_dict() -> None:
    """When the effect has no payload yet, set_async seeds a new one."""
    effect = Effect()
    assert effect.payload == ""

    effect.set_async(delay_seconds=5)

    assert json.loads(effect.payload) == {ASYNC_PROPS_KEY: {"delay_seconds": 5}}


def test_non_json_payload_raises_descriptive_error() -> None:
    """A non-JSON effect payload raises a clear ValueError, not JSONDecodeError."""
    effect = _TestEffect().apply()
    effect.payload = "Hello, world!"
    with pytest.raises(ValueError, match="Effect payload must be valid JSON to use set_async"):
        effect.set_async(delay_seconds=1)


def test_preserves_existing_payload_data() -> None:
    """Non-async payload data is left alone when set_async is called."""
    effect = _TestEffect().apply()
    payload = json.loads(effect.payload)
    assert payload == {"data": {}}

    effect.set_async(delay_seconds=10)
    payload = json.loads(effect.payload)
    assert payload["data"] == {}
    assert payload[ASYNC_PROPS_KEY] == {"delay_seconds": 10}


def test_set_async_mutates_underlying_protobuf() -> None:
    """Changes made via set_async are visible on the to_proto result."""
    effect = _TestEffect().apply().set_async(delay_seconds=7)
    pb_payload = json.loads(effect.to_proto().payload)
    assert pb_payload[ASYNC_PROPS_KEY] == {"delay_seconds": 7}
