from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.clients import CanvasFhir

MOCK_CREDENTIALS = {
    "access_token": "test_token",
    "expires_in": 3600,
    "refresh_token": "test_refresh",
    "scope": "test_scope",
    "token_type": "Bearer",
}


@pytest.fixture
def mock_get_cache() -> Generator[MagicMock, None, None]:
    """Mock the get_cache method of the CanvasFhir instance."""
    with patch("canvas_sdk.clients.canvas_fhir.client.get_cache") as mock:
        yield mock


@pytest.fixture
def mock_post() -> Generator[MagicMock, None, None]:
    """Mock the post method of the Http instance."""
    with patch("canvas_sdk.utils.http.Http.post") as mock:
        yield mock


def test__api_base_url(mock_get_cache: MagicMock) -> None:
    """Test the defined URL of the CanvasFhir instance."""
    tested = CanvasFhir(client_id="test", client_secret="test", customer_identifier="test")
    result = tested._base_url
    expected = "https://fumage-test.canvasmedical.com"
    assert result == expected


def test__get_credentials_without_cached_credentials(
    mock_get_cache: MagicMock, mock_post: MagicMock
) -> None:
    """Test the _get_credentials method of the CanvasFhir instance without cached credentials."""
    mock_get_cache.return_value.get.return_value = None
    mock_post.return_value = MagicMock(status_code=200, json=lambda: MOCK_CREDENTIALS)

    tested = CanvasFhir(client_id="test", client_secret="test", customer_identifier="test")
    result = tested._get_credentials()
    expected = MOCK_CREDENTIALS
    assert result == expected


def test__get_credentials_with_cached_credentials(
    mock_get_cache: MagicMock, mock_post: MagicMock
) -> None:
    """Test the _get_credentials method of the CanvasFhir instance with cached credentials."""
    mock_get_cache.return_value.get.return_value = MOCK_CREDENTIALS

    tested = CanvasFhir(client_id="test", client_secret="test", customer_identifier="test")
    result = tested._get_credentials()
    expected = MOCK_CREDENTIALS

    mock_post.assert_not_called()
    assert result == expected
