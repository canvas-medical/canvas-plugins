import jsonschema
import pytest
from jsonschema import ValidationError

from canvas_cli.utils.validators import validate_manifest_file


@pytest.fixture
def handler_manifest_example() -> dict:
    """Return a valid handler manifest example."""
    return {
        "sdk_version": "0.3.1",
        "plugin_version": "1.0.1",
        "name": "Prompt to prescribe when assessing condition",
        "description": "To assist in ....",
        "components": {
            "handlers": [
                {
                    "class": "prompt_to_prescribe.handlers.prompt_when_assessing.PromptWhenAssessing",
                    "description": "probably the same as the plugin's description",
                    "data_access": {
                        "event": "",
                        "read": ["conditions"],
                        "write": ["commands"],
                    },
                }
            ]
        },
        "tags": {"patient_sourcing_and_intake": ["symptom_triage"]},
        "references": [],
        "license": "",
        "diagram": False,
        "readme": "README.MD",
    }


def _make_application_manifest(scope: str) -> dict:
    """Return a valid manifest with a single application using the given scope."""
    return {
        "sdk_version": "0.1.4",
        "plugin_version": "0.0.1",
        "name": "test_plugin",
        "description": "A test plugin",
        "components": {
            "applications": [
                {
                    "class": "test_plugin.apps.my_app:MyApp",
                    "name": "My App",
                    "description": "A test application",
                    "scope": scope,
                    "icon": "assets/icon.png",
                }
            ]
        },
        "tags": {},
        "license": "",
        "readme": "README.md",
    }


def test_manifest_file_schema(handler_manifest_example: dict) -> None:
    """Test that no exception raised when a valid manifest file is validated."""
    validate_manifest_file(handler_manifest_example)


@pytest.mark.parametrize(
    "scope",
    [
        "provider_companion",
        "provider_companion_global",
        "provider_companion_patient_specific",
        "provider_companion_note_specific",
        "patient_specific",
        "global",
        "provider_menu_item",
        "portal_menu_item",
        "full_chart",
    ],
    ids=lambda s: s,
)
def test_manifest_validates_application_scope(scope: str) -> None:
    """Test that all supported application scopes pass manifest validation."""
    validate_manifest_file(_make_application_manifest(scope))


def test_manifest_rejects_invalid_application_scope() -> None:
    """Test that an unrecognized application scope fails manifest validation."""
    with pytest.raises(ValidationError, match="is not one of"):
        validate_manifest_file(_make_application_manifest("not_a_real_scope"))


def test_manifest_with_variables(handler_manifest_example: dict) -> None:
    """Test that variables array with name and sensitive fields validates."""
    handler_manifest_example["variables"] = [
        {"name": "OPENAI_API_KEY", "sensitive": True},
        {"name": "WEBHOOK_URL", "sensitive": False},
        {"name": "PLAIN_VAR"},
    ]
    validate_manifest_file(handler_manifest_example)


def test_manifest_with_legacy_secrets(
    handler_manifest_example: dict, capsys: pytest.CaptureFixture
) -> None:
    """Test that legacy secrets array still validates with a deprecation warning."""
    handler_manifest_example["secrets"] = ["MY_SECRET"]
    validate_manifest_file(handler_manifest_example)
    captured = capsys.readouterr()
    assert "deprecated" in captured.out.lower()


def test_manifest_with_empty_variables(handler_manifest_example: dict) -> None:
    """Test that an empty variables array validates."""
    handler_manifest_example["variables"] = []
    validate_manifest_file(handler_manifest_example)


def test_manifest_variable_with_default(handler_manifest_example: dict) -> None:
    """Test that non-sensitive variables can have a default value."""
    handler_manifest_example["variables"] = [
        {"name": "WEBHOOK_URL", "default": "https://example.com/webhook"},
        {"name": "RETRY_COUNT", "sensitive": False, "default": "3"},
    ]
    validate_manifest_file(handler_manifest_example)


def test_manifest_sensitive_variable_rejects_default(handler_manifest_example: dict) -> None:
    """Test that sensitive variables cannot have a default value."""
    handler_manifest_example["variables"] = [
        {"name": "API_KEY", "sensitive": True, "default": "secret123"},
    ]
    with pytest.raises(jsonschema.ValidationError):
        validate_manifest_file(handler_manifest_example)


def test_manifest_variable_rejects_extra_fields(handler_manifest_example: dict) -> None:
    """Test that variables with unknown fields are rejected."""
    handler_manifest_example["variables"] = [
        {"name": "KEY", "sensitive": True, "extra": "bad"},
    ]
    with pytest.raises(jsonschema.ValidationError):
        validate_manifest_file(handler_manifest_example)
