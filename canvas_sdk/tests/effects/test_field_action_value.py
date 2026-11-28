import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.field_action_value import FieldActionValue


def test_apply_produces_field_action_value_effect() -> None:
    """apply() produces an effect of type FIELD_ACTION_VALUE."""
    effect = FieldActionValue(value="Take 1 tablet by mouth daily").apply()
    assert effect.type == EffectType.FIELD_ACTION_VALUE


def test_payload_is_the_value() -> None:
    """The payload carries the value under data."""
    effect = FieldActionValue(value="Take 1 tablet by mouth daily").apply()
    assert json.loads(effect.payload) == {"data": {"value": "Take 1 tablet by mouth daily"}}


def test_payload_allows_null_value() -> None:
    """A None value is sent as null."""
    effect = FieldActionValue(value=None).apply()
    assert json.loads(effect.payload) == {"data": {"value": None}}


def test_value_is_required() -> None:
    """Omitting value raises a validation error."""
    with pytest.raises(ValidationError):
        FieldActionValue()  # type: ignore[call-arg]


def test_value_must_be_a_string() -> None:
    """A non-string value raises a validation error."""
    with pytest.raises(ValidationError):
        FieldActionValue(value=123)  # type: ignore[arg-type]
