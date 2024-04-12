from unittest.mock import MagicMock, patch

import pytest

from canvas_cli.apps.auth.utils import get_api_client_credentials
from canvas_cli.utils.context.context import CLIContext
from canvas_cli.utils.validators import get_default_host, validate_manifest_file


def test_get_default_host() -> None:
    """Test get_default_host returns the context's default host if needed."""
    mock_host = "mock_host"

    assert get_default_host(mock_host) == mock_host

    with patch.object(CLIContext, "default_host", new_callable=lambda: mock_host):
        assert get_default_host(None) == mock_host


@patch("keyring.get_password")
def test_get_api_client_credentials(mock_get_password: MagicMock) -> None:
    """Test get_api_client_credentials returns the given api_key or fetches from `get_password`."""
    mock_get_password.return_value = "a_password"

    mock_host = "a_host"
    assert get_api_client_credentials(mock_host, None, None) == "a_password"
    assert get_api_client_credentials(mock_host, None, "secret") == "a_password"
    assert get_api_client_credentials(mock_host, "id", None) == "a_password"
    assert (
        get_api_client_credentials(mock_host, "id", "secret") == "client_id=id&client_secret=secret"
    )


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
                        "event": "assess_condition_selected",
                        "read": ["conditions"],
                        "write": ["commands"],
                    },
                }
            ]
        },
    }


def test_manifest_file_schema(protocol_manifest_example: dict) -> None:
    """Test that no exception raised when a valid manifest file is validated"""
    validate_manifest_file(protocol_manifest_example)
