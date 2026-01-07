import json

from canvas_sdk.effects.validation import EventValidationError, ValidationError


def test_event_validation_error_payload() -> None:
    """Test that EventValidationError returns correct payload."""
    error_msg1 = "Invalid event data"
    error_msg2 = "Missing required field"
    effect = EventValidationError(errors=[ValidationError(message=error_msg1)])
    effect.add_error(error_msg2)
    payload = json.loads(effect.apply().payload)
    assert payload["errors"][0]["message"] == error_msg1
    assert payload["errors"][1]["message"] == error_msg2


def test_event_validation_error_single_message() -> None:
    """Test EventValidationError with a single error message."""
    effect = EventValidationError(errors=[ValidationError(message="foo ")])
    payload = json.loads(effect.apply().payload)
    assert payload["errors"][0]["message"] == "foo"


def test_event_validation_error_add_error() -> None:
    """Test add_error appends a new error message."""
    effect = EventValidationError(errors=[ValidationError(message="first")])
    effect.add_error("second")
    payload = json.loads(effect.apply().payload)
    assert payload["errors"][1]["message"] == "second"


def test_event_validation_error_repr() -> None:
    """Test __repr__ includes error messages."""
    effect = EventValidationError(errors=[ValidationError(message="bad")])
    rep = repr(effect)
    assert "bad" in rep
