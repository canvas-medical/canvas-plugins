from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from canvas_cli.apps.auth import get_or_request_api_token


@pytest.fixture
def valid_token_response() -> Any:
    """Returns a valid token response."""

    class TokenResponse:
        status_code = 200

        def json(self) -> dict:
            return {"access_token": "a-valid-api-token", "expires_in": 3600}

    return TokenResponse()


@pytest.fixture
def error_token_response() -> Any:
    """Returns an error token response."""

    class TokenResponse:
        status_code = 500

    return TokenResponse()


@pytest.fixture
def expired_token_response() -> Any:
    """Returns an expired token response."""

    class TokenResponse:
        status_code = 200

        def json(self) -> dict:
            return {"access_token": "a-valid-api-token", "expires_in": -1}

    return TokenResponse()


@patch("canvas_cli.apps.auth.utils.get_token")
@patch("requests.Session.post")
def test_get_or_request_api_token_uses_stored_token(
    mock_post: MagicMock,
    mock_get_token: MagicMock,
    valid_token_response: Any,
) -> None:
    """Test that get_or_request_api_token uses a stored token if it is valid."""
    mock_get_token.return_value = "a-stored-valid-token"
    mock_post.return_value = valid_token_response

    token = get_or_request_api_token("http://localhost:8000")

    assert token == "a-stored-valid-token"
    mock_post.assert_not_called()


@patch("canvas_cli.apps.auth.utils.set_token")
@patch("canvas_cli.apps.auth.utils.get_token")
@patch("requests.Session.post")
@patch("canvas_cli.apps.auth.utils.get_api_client_credentials")
def test_get_or_request_api_token_requests_token_if_none_stored(
    mock_client_credentials: MagicMock,
    mock_post: MagicMock,
    mock_get_token: MagicMock,
    mock_set_token: MagicMock,
    valid_token_response: Any,
    freezer: None,
) -> None:
    """Test that get_or_request_api_token requests a new token if none is stored."""
    mock_client_credentials.return_value = "client_id=id&client_secret=secret"
    mock_get_token.return_value = None
    mock_post.return_value = valid_token_response

    token = get_or_request_api_token("http://localhost:8000")

    assert token == "a-valid-api-token"
    mock_post.assert_called_once_with(
        "http://localhost:8000/auth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        json=None,
        data="grant_type=client_credentials&scope=system/Plugins.*&client_id=id&client_secret=secret",
        timeout=30,
    )
    mock_set_token.assert_called_with(
        "http://localhost:8000",
        "a-valid-api-token",
        datetime.now() + timedelta(seconds=valid_token_response.json()["expires_in"]),
    )


@patch("canvas_cli.apps.auth.utils.get_token")
@patch("requests.Session.post")
@patch("canvas_cli.apps.auth.utils.get_api_client_credentials")
def test_get_or_request_api_token_raises_exception_if_error_token_response(
    mock_client_credentials: MagicMock,
    mock_post: MagicMock,
    mock_get_token: MagicMock,
    error_token_response: Any,
) -> None:
    """Test that get_or_request_api_token raises an exception if an error token response is received."""
    mock_client_credentials.return_value = "client_id=id&client_secret=secret"
    mock_get_token.return_value = None
    mock_post.return_value = error_token_response

    with pytest.raises(Exception) as e:
        get_or_request_api_token("http://localhost:8000")

    assert "Unable to get a valid access token from the given host 'http://localhost:8000'" in repr(
        e
    )

    mock_post.assert_called_once_with(
        "http://localhost:8000/auth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        json=None,
        data="grant_type=client_credentials&scope=system/Plugins.*&client_id=id&client_secret=secret",
        timeout=30,
    )


@patch("canvas_cli.apps.auth.utils.get_token")
@patch("requests.Session.post")
@patch("canvas_cli.apps.auth.utils.get_api_client_credentials")
def test_get_or_request_api_token_raises_exception_if_expired_token(
    mock_client_credentials: MagicMock,
    mock_post: MagicMock,
    mock_get_token: MagicMock,
    expired_token_response: Any,
) -> None:
    """Test that get_or_request_api_token raises an exception if an expired token is received."""
    mock_client_credentials.return_value = "client_id=id&client_secret=secret"
    mock_get_token.return_value = None
    mock_post.return_value = expired_token_response

    with pytest.raises(Exception) as e:
        get_or_request_api_token("http://localhost:8000")

    assert (
        "A valid token could not be acquired from the given host 'http://localhost:8000'" in repr(e)
    )

    mock_post.assert_called_once_with(
        "http://localhost:8000/auth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        json=None,
        data="grant_type=client_credentials&scope=system/Plugins.*&client_id=id&client_secret=secret",
        timeout=30,
    )
