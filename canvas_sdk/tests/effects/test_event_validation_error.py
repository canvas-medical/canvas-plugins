import json

import pytest

from canvas_sdk.effects.validation import EventValidationError, ValidationError
from canvas_sdk.effects.validation.base import _BaseValidationErrorEffect


def test_event_validation_error_payload() -> None:
    """Test that EventValidationError returns correct payload."""
    error_msg1 = "Invalid event data"
    error_msg2 = "Missing required field"
    effect = EventValidationError(errors=[ValidationError(message=error_msg1)])
    effect.add_error(error_msg2)
    payload = json.loads(effect.apply().payload)
    assert payload["data"]["errors"][0]["message"] == error_msg1
    assert payload["data"]["errors"][1]["message"] == error_msg2


def test_event_validation_error_single_message() -> None:
    """Test EventValidationError with a single error message."""
    effect = EventValidationError(errors=[ValidationError(message="foo ")])
    payload = json.loads(effect.apply().payload)
    assert payload["data"]["errors"][0]["message"] == "foo"


def test_event_validation_error_add_error() -> None:
    """Test add_error appends a new error message."""
    effect = EventValidationError(errors=[ValidationError(message="first")])
    effect.add_error("second")
    payload = json.loads(effect.apply().payload)
    assert payload["data"]["errors"][1]["message"] == "second"


def test_event_validation_error_repr() -> None:
    """Test __repr__ includes error messages."""
    effect = EventValidationError(errors=[ValidationError(message="bad")])
    rep = repr(effect)
    assert "bad" in rep


def test_validation_error_init_and_repr() -> None:
    """Test ValidationError initialization, whitespace trimming, and repr. Also checks ValueError for empty messages."""
    err = ValidationError("foo")
    assert err.message == "foo"
    assert "foo" in repr(err)

    err2 = ValidationError("  bar  ")
    assert err2.message == "bar"

    with pytest.raises(ValueError):
        ValidationError("")
    with pytest.raises(ValueError):
        ValidationError("   ")


def test_validation_error_to_dict() -> None:
    """Test ValidationError.to_dict returns correct dictionary."""
    err = ValidationError("baz")
    assert err.to_dict() == {"message": "baz"}


def test_base_validation_error_effect_add_error_and_payload() -> None:
    """Test adding errors to _BaseValidationErrorEffect and correct effect_payload output."""
    effect = _BaseValidationErrorEffect()
    effect.add_error("err1").add_error(ValidationError("err2"))
    payload = effect.effect_payload
    assert payload == {"data": {"errors": [{"message": "err1"}, {"message": "err2"}]}}

    # Test empty errors list
    effect2 = _BaseValidationErrorEffect()
    assert effect2.effect_payload == {"data": {"errors": []}}
