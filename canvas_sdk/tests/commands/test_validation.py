import json

import pytest
from pydantic import ValidationError as PydanticValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.validation import CommandValidationErrorEffect, ValidationError

# ValidationError tests


def test_validation_error_initialization_with_valid_message() -> None:
    """Test that ValidationError can be initialized with a valid message."""
    error = ValidationError(message="This is an error")
    assert error.message == "This is an error"


def test_validation_error_initialization_strips_whitespace() -> None:
    """Test that ValidationError strips leading/trailing whitespace from message."""
    error = ValidationError(message="  This is an error  ")
    assert error.message == "This is an error"


def test_validation_error_initialization_with_empty_message_raises_error() -> None:
    """Test that ValidationError raises ValueError with empty message."""
    with pytest.raises(ValueError, match="Error message cannot be empty"):
        ValidationError(message="")


def test_validation_error_initialization_with_whitespace_only_message_raises_error() -> None:
    """Test that ValidationError raises ValueError with whitespace-only message."""
    with pytest.raises(ValueError, match="Error message cannot be empty"):
        ValidationError(message="   ")


def test_validation_error_to_dict_returns_correct_format() -> None:
    """Test that to_dict() returns the correct dictionary format."""
    error = ValidationError(message="Test error")
    result = error.to_dict()
    assert result == {"message": "Test error"}
    assert isinstance(result, dict)


def test_validation_error_repr_returns_correct_format() -> None:
    """Test that __repr__() returns the correct string representation."""
    error = ValidationError(message="Test error")
    result = repr(error)
    assert result == "ValidationError(message='Test error')"


# CommandValidationErrorEffect tests


def test_command_validation_error_effect_initialization_with_no_errors() -> None:
    """Test that CommandValidationErrorEffect can be initialized with no errors."""
    effect = CommandValidationErrorEffect()
    assert effect.errors == []
    assert isinstance(effect.errors, list)


def test_command_validation_error_effect_initialization_with_errors_list() -> None:
    """Test that CommandValidationErrorEffect can be initialized with a list of errors."""
    errors = [
        ValidationError(message="Error 1"),
        ValidationError(message="Error 2"),
    ]
    effect = CommandValidationErrorEffect(errors=errors)
    assert len(effect.errors) == 2
    assert effect.errors[0].message == "Error 1"
    assert effect.errors[1].message == "Error 2"


def test_command_validation_error_effect_add_error_appends_error_to_list() -> None:
    """Test that add_error() appends an error to the errors list."""
    effect = CommandValidationErrorEffect()
    effect.add_error("Test error")
    assert len(effect.errors) == 1
    assert effect.errors[0].message == "Test error"


def test_command_validation_error_effect_add_error_with_multiple_errors() -> None:
    """Test that add_error() can be called multiple times."""
    effect = CommandValidationErrorEffect()
    effect.add_error("Error 1")
    effect.add_error("Error 2")
    effect.add_error("Error 3")
    assert len(effect.errors) == 3
    assert effect.errors[0].message == "Error 1"
    assert effect.errors[1].message == "Error 2"
    assert effect.errors[2].message == "Error 3"


def test_command_validation_error_effect_add_error_returns_self_for_chaining() -> None:
    """Test that add_error() returns self for method chaining."""
    effect = CommandValidationErrorEffect()
    result = effect.add_error("Error 1")
    assert result is effect


def test_command_validation_error_effect_add_error_method_chaining() -> None:
    """Test that add_error() supports method chaining."""
    effect = CommandValidationErrorEffect()
    effect.add_error("Error 1").add_error("Error 2").add_error("Error 3")
    assert len(effect.errors) == 3
    assert effect.errors[0].message == "Error 1"
    assert effect.errors[1].message == "Error 2"
    assert effect.errors[2].message == "Error 3"


def test_command_validation_error_effect_add_error_with_empty_message_raises_error() -> None:
    """Test that add_error() raises ValueError with empty message."""
    effect = CommandValidationErrorEffect()
    with pytest.raises(ValueError, match="Error message cannot be empty"):
        effect.add_error("")


def test_command_validation_error_effect_add_error_strips_whitespace() -> None:
    """Test that add_error() strips whitespace from message."""
    effect = CommandValidationErrorEffect()
    effect.add_error("  Test error  ")
    assert effect.errors[0].message == "Test error"


def test_command_validation_error_effect_values_property_returns_correct_format() -> None:
    """Test that values property returns the correct format."""
    effect = CommandValidationErrorEffect()
    effect.add_error("Error 1")
    effect.add_error("Error 2")
    result = effect.values
    assert result == {
        "errors": [
            {"message": "Error 1"},
            {"message": "Error 2"},
        ]
    }


def test_command_validation_error_effect_values_property_with_no_errors() -> None:
    """Test that values property returns empty list with no errors."""
    effect = CommandValidationErrorEffect()
    result = effect.values
    assert result == {"errors": []}


def test_command_validation_error_effect_effect_payload_returns_correct_format() -> None:
    """Test that effect_payload property returns the correct format."""
    effect = CommandValidationErrorEffect()
    effect.add_error("Error 1")
    effect.add_error("Error 2")
    result = effect.effect_payload
    assert result == {
        "data": {
            "errors": [
                {"message": "Error 1"},
                {"message": "Error 2"},
            ]
        }
    }


def test_command_validation_error_effect_apply_returns_effect_with_correct_type() -> None:
    """Test that apply() returns an Effect with the correct type."""
    effect = CommandValidationErrorEffect()
    effect.add_error("Test error")
    result = effect.apply()
    assert result.type == EffectType.COMMAND_VALIDATION_ERRORS


def test_command_validation_error_effect_apply_returns_effect_with_correct_payload() -> None:
    """Test that apply() returns an Effect with the correct payload."""
    effect = CommandValidationErrorEffect()
    effect.add_error("Error 1")
    effect.add_error("Error 2")
    result = effect.apply()

    payload = json.loads(result.payload)
    assert payload == {
        "data": {
            "errors": [
                {"message": "Error 1"},
                {"message": "Error 2"},
            ]
        }
    }


def test_command_validation_error_effect_apply_with_no_errors_returns_empty_list() -> None:
    """Test that apply() with no errors returns an effect with empty error list."""
    effect = CommandValidationErrorEffect()
    result = effect.apply()

    payload = json.loads(result.payload)
    assert payload == {"data": {"errors": []}}


def test_command_validation_error_effect_initialization_with_invalid_errors_type_raises_error() -> (
    None
):
    """Test that initialization with non-list errors raises ValidationError."""
    with pytest.raises(PydanticValidationError):
        CommandValidationErrorEffect(errors="not a list")  # type: ignore


def test_command_validation_error_effect_initialization_with_invalid_error_objects_raises_error() -> (
    None
):
    """Test that initialization with non-ValidationError objects raises ValidationError."""
    with pytest.raises(PydanticValidationError):
        CommandValidationErrorEffect(errors=["not a ValidationError"])  # type: ignore


def test_command_validation_error_effect_meta_class_has_correct_effect_type() -> None:
    """Test that the Meta class has the correct effect type."""
    assert CommandValidationErrorEffect.Meta.effect_type == EffectType.COMMAND_VALIDATION_ERRORS


def test_command_validation_error_effect_multiple_effects_with_same_errors() -> None:
    """Test that multiple effects can be created with the same error messages."""
    effect1 = CommandValidationErrorEffect()
    effect1.add_error("Duplicate error")

    effect2 = CommandValidationErrorEffect()
    effect2.add_error("Duplicate error")

    assert effect1.errors[0].message == effect2.errors[0].message
    assert effect1.errors is not effect2.errors  # Different lists


def test_command_validation_error_effect_real_world_usage_example() -> None:
    """Test a real-world usage example similar to what would be in a protocol."""
    # Simulating a protocol validation
    effect = CommandValidationErrorEffect()

    # Add multiple validation errors
    narrative = ""
    if not narrative.strip():
        effect.add_error("Narrative is required")

    dosage = -5
    if dosage <= 0:
        effect.add_error("Dosage must be a positive number")

    frequency = None
    if frequency is None:
        effect.add_error("Frequency is required")

    # Apply and check result
    result = effect.apply()
    payload = json.loads(result.payload)

    assert len(payload["data"]["errors"]) == 3
    assert payload["data"]["errors"][0]["message"] == "Narrative is required"
    assert payload["data"]["errors"][1]["message"] == "Dosage must be a positive number"
    assert payload["data"]["errors"][2]["message"] == "Frequency is required"
