from unittest.mock import MagicMock, patch

from canvas_cli.utils.context.context import CLIContext
from canvas_cli.utils.validators import get_api_key, get_default_host


def test_get_default_host() -> None:
    """Test get_default_host returns the context's default host if needed."""
    mock_host = "mock_host"

    assert get_default_host(mock_host) == mock_host

    with patch.object(CLIContext, "default_host", new_callable=lambda: mock_host):
        assert get_default_host(None) == mock_host


@patch("keyring.get_password")
def test_get_api_key(mock_get_password: MagicMock) -> None:
    """Test get_api_key returns the given api_key or fetches from `get_password`."""
    mock_get_password.return_value = "a_password"

    mock_host = "a_host"
    assert get_api_key(mock_host, None) == "a_password"
    assert get_api_key(mock_host, "an_api_key") == "an_api_key"
