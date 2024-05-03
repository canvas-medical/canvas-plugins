import pytest

from canvas_cli.utils.validators import validate_manifest_file


@pytest.fixture
def protocol_manifest_example() -> dict:
    return {
        "sdk_version": "0.3.1",
        "plugin_version": "1.0.1",
        "name": "Prompt to prescribe when assessing condition",
        "description": "To assist in ....",
        "components": {
            "protocols": [
                {
                    "class": "prompt_to_prescribe.protocols.prompt_when_assessing.PromptWhenAssessing",
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


def test_manifest_file_schema(protocol_manifest_example: dict) -> None:
    """Test that no exception raised when a valid manifest file is validated"""
    validate_manifest_file(protocol_manifest_example)
