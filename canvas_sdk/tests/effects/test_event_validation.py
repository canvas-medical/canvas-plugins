import json

from canvas_sdk.effects.event_validation_error import EventValidationError


def test_event_validation_error_payload() -> None:
    """Test that EventValidationError returns correct payload."""
    error_msg = "Invalid event data"
    effect = EventValidationError(message=error_msg).apply()
    payload = json.loads(effect.payload)

    assert payload["message"] == error_msg
