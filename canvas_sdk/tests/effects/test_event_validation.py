import json

from canvas_sdk.effects.validation import EventValidationError, ValidationError


def test_event_validation_error_payload() -> None:
    """Test that EventValidationError returns correct payload."""
    error_msg1 = "Invalid event data"
    error_msg2 = "Missing required field"
    effect = EventValidationError(
        errors=[ValidationError(message=error_msg1), ValidationError(message=error_msg2)]
    ).apply()
    payload = json.loads(effect.payload)

    assert payload["errors"][0]["message"] == error_msg1
    assert payload["errors"][1]["message"] == error_msg2
