import stat
import threading
import time as time_module
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests
import typer

from canvas_cli.apps.auth import get_or_request_api_token, oauth


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


# --- oauth.py tests ---


@pytest.fixture
def tmp_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect oauth.CONFIG_PATH to a temp file."""
    path = tmp_path / "credentials.ini"
    monkeypatch.setattr(oauth, "CONFIG_PATH", path)
    return path


def _token_response(status: int = 200, body: dict[str, Any] | None = None) -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status
    resp.text = "" if body is None else str(body)
    resp.json.return_value = body or {}
    return resp


def test_read_section_missing_file(tmp_config: Path) -> None:
    """Test that Read section missing file."""
    assert oauth._read_section() == {}


def test_read_section_file_without_section(tmp_config: Path) -> None:
    """Test that Read section file without section."""
    tmp_config.write_text("[other]\nclient_id = abc\n")
    assert oauth._read_section() == {}


def test_read_section_returns_section(tmp_config: Path) -> None:
    """Test that Read section returns section."""
    tmp_config.write_text(
        "[control-room]\naccess_token = AT\nrefresh_token = RT\nexpires_at = 123\n"
    )
    section = oauth._read_section()
    assert section["access_token"] == "AT"
    assert section["refresh_token"] == "RT"
    assert section["expires_at"] == "123"


def test_replace_section_appends_when_missing() -> None:
    """Test that Replace section appends when missing."""
    text = "[acme]\nkey = val\n"
    body = "[control-room]\naccess_token = AT\n"
    out = oauth._replace_section(text, "control-room", body)
    assert out.startswith("[acme]\nkey = val\n")
    assert out.endswith("[control-room]\naccess_token = AT\n")


def test_replace_section_appends_to_empty_text() -> None:
    """Test that Replace section appends to empty text."""
    body = "[control-room]\naccess_token = AT\n"
    out = oauth._replace_section("", "control-room", body)
    assert out == body


def test_replace_section_appends_when_no_trailing_newline() -> None:
    """Test that Replace section appends when no trailing newline."""
    text = "[acme]\nkey = val"
    body = "[control-room]\naccess_token = AT\n"
    out = oauth._replace_section(text, "control-room", body)
    assert "[acme]\nkey = val\n" in out
    assert out.endswith(body)


def test_replace_section_replaces_in_place() -> None:
    """Test that Replace section replaces in place."""
    text = (
        "[acme]\nkey = val\n\n"
        "[control-room]\naccess_token = OLD\nrefresh_token = OLDR\n\n"
        "[localhost]\nfoo = bar\n"
    )
    body = "[control-room]\naccess_token = NEW\nrefresh_token = NEWR\n"
    out = oauth._replace_section(text, "control-room", body)
    assert "access_token = NEW" in out
    assert "access_token = OLD" not in out
    assert "[acme]" in out and "[localhost]" in out


def test_replace_section_preserves_comments() -> None:
    """Test that Replace section preserves comments."""
    text = "; my note\n# another note\n[acme]\nkey = val\n"
    body = "[control-room]\naccess_token = AT\n"
    out = oauth._replace_section(text, "control-room", body)
    assert "; my note" in out
    assert "# another note" in out


def test_replace_section_deletes() -> None:
    """Test that Replace section deletes."""
    text = "[acme]\nkey = val\n\n[control-room]\naccess_token = AT\n"
    out = oauth._replace_section(text, "control-room", None)
    assert "control-room" not in out
    assert "[acme]" in out


def test_replace_section_delete_when_missing_is_noop() -> None:
    """Test that Replace section delete when missing is noop."""
    text = "[acme]\nkey = val\n"
    out = oauth._replace_section(text, "control-room", None)
    assert out == text


def test_write_section_creates_file_with_0600(tmp_config: Path) -> None:
    """Test that Write section creates file with 0600."""
    oauth._write_section({"access_token": "AT", "refresh_token": "RT", "expires_at": 1730000000})
    assert tmp_config.exists()
    text = tmp_config.read_text()
    assert "[control-room]" in text
    assert "access_token = AT" in text
    assert "expires_at = 1730000000" in text
    mode = tmp_config.stat().st_mode & 0o777
    assert mode == stat.S_IRUSR | stat.S_IWUSR


def test_write_section_preserves_existing_file(tmp_config: Path) -> None:
    """Test that Write section preserves existing file."""
    tmp_config.write_text("; comment\n[acme]\nclient_id = abc\n")
    oauth._write_section({"access_token": "AT", "refresh_token": "RT", "expires_at": 1})
    text = tmp_config.read_text()
    assert "; comment" in text
    assert "[acme]" in text
    assert "[control-room]" in text


def test_delete_section_no_file(tmp_config: Path) -> None:
    """Test that Delete section no file."""
    oauth._delete_section()  # should not raise


def test_delete_section_no_section(tmp_config: Path) -> None:
    """Test that Delete section no section."""
    tmp_config.write_text("[acme]\nclient_id = abc\n")
    oauth._delete_section()
    assert tmp_config.read_text() == "[acme]\nclient_id = abc\n"


def test_delete_section_removes_section(tmp_config: Path) -> None:
    """Test that Delete section removes section."""
    tmp_config.write_text("[acme]\nclient_id = abc\n\n[control-room]\naccess_token = AT\n")
    oauth._delete_section()
    text = tmp_config.read_text()
    assert "control-room" not in text
    assert "[acme]" in text


def test_save_tokens_computes_expires_at(tmp_config: Path) -> None:
    """Test that Save tokens computes expires at."""
    with patch.object(oauth.time, "time", return_value=1_000_000.0):
        oauth._save_tokens({"access_token": "AT", "refresh_token": "RT", "expires_in": 3600})
    section = oauth._read_section()
    assert section["access_token"] == "AT"
    assert section["expires_at"] == str(1_000_000 + 3600)


def test_save_tokens_handles_missing_expires_in(tmp_config: Path) -> None:
    """Test that Save tokens handles missing expires in."""
    with patch.object(oauth.time, "time", return_value=500.0):
        oauth._save_tokens({"access_token": "AT"})
    section = oauth._read_section()
    assert section["expires_at"] == "500"
    assert section["refresh_token"] == ""


def test_generate_pkce_returns_valid_pair() -> None:
    """Test that Generate pkce returns valid pair."""
    import base64
    import hashlib

    verifier, challenge = oauth._generate_pkce()
    assert isinstance(verifier, str) and isinstance(challenge, str)
    assert "=" not in challenge
    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )
    assert challenge == expected


def test_get_access_token_no_creds(tmp_config: Path) -> None:
    """Test that Get access token no creds."""
    assert oauth.get_access_token() is None


def test_get_access_token_returns_when_not_expired(tmp_config: Path) -> None:
    """Test that Get access token returns when not expired."""
    far_future = int(time_module.time()) + 3600
    tmp_config.write_text(
        f"[control-room]\naccess_token = AT\nrefresh_token = RT\nexpires_at = {far_future}\n"
    )
    assert oauth.get_access_token() == "AT"


def test_get_access_token_no_expires_at_returns_token(tmp_config: Path) -> None:
    """Test that Get access token no expires at returns token."""
    tmp_config.write_text("[control-room]\naccess_token = AT\nrefresh_token = RT\nexpires_at = 0\n")
    assert oauth.get_access_token() == "AT"


@patch("canvas_cli.apps.auth.oauth.refresh_access_token")
def test_get_access_token_refreshes_when_near_expiry(
    mock_refresh: MagicMock, tmp_config: Path
) -> None:
    """Test that Get access token refreshes when near expiry."""
    near_expiry = int(time_module.time()) + 30  # within 60s leeway
    tmp_config.write_text(
        f"[control-room]\naccess_token = OLD\nrefresh_token = RT\nexpires_at = {near_expiry}\n"
    )
    mock_refresh.return_value = "NEW"
    assert oauth.get_access_token() == "NEW"
    mock_refresh.assert_called_once()


def test_refresh_access_token_no_refresh_token(tmp_config: Path) -> None:
    """Test that Refresh access token no refresh token."""
    assert oauth.refresh_access_token() is None


@patch("canvas_cli.apps.auth.oauth.requests.post")
def test_refresh_access_token_success(mock_post: MagicMock, tmp_config: Path) -> None:
    """Test that Refresh access token success."""
    tmp_config.write_text(
        "[control-room]\naccess_token = OLD\nrefresh_token = RT\nexpires_at = 0\n"
    )
    mock_post.return_value = _token_response(
        200, {"access_token": "NEW", "refresh_token": "NEWR", "expires_in": 3600}
    )
    assert oauth.refresh_access_token() == "NEW"
    section = oauth._read_section()
    assert section["access_token"] == "NEW"
    assert section["refresh_token"] == "NEWR"


@patch("canvas_cli.apps.auth.oauth.requests.post")
def test_refresh_access_token_network_error(mock_post: MagicMock, tmp_config: Path) -> None:
    """Test that Refresh access token network error."""
    tmp_config.write_text(
        "[control-room]\naccess_token = OLD\nrefresh_token = RT\nexpires_at = 0\n"
    )
    mock_post.side_effect = requests.RequestException("boom")
    assert oauth.refresh_access_token() is None


@patch("canvas_cli.apps.auth.oauth.requests.post")
def test_refresh_access_token_non_200(mock_post: MagicMock, tmp_config: Path) -> None:
    """Test that Refresh access token non 200."""
    tmp_config.write_text(
        "[control-room]\naccess_token = OLD\nrefresh_token = RT\nexpires_at = 0\n"
    )
    mock_post.return_value = _token_response(500)
    assert oauth.refresh_access_token() is None


def test_logout_no_credentials(tmp_config: Path, capsys: pytest.CaptureFixture) -> None:
    """Test that Logout no credentials."""
    oauth.logout()
    assert "No credentials found." in capsys.readouterr().out


@patch("canvas_cli.apps.auth.oauth.requests.post")
def test_logout_revokes_and_clears(
    mock_post: MagicMock, tmp_config: Path, capsys: pytest.CaptureFixture
) -> None:
    """Test that Logout revokes and clears."""
    tmp_config.write_text(
        "[acme]\nclient_id = abc\n\n[control-room]\naccess_token = AT\n"
        "refresh_token = RT\nexpires_at = 1\n"
    )
    oauth.logout()
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0].endswith("/oauth/revoke_token/")
    assert kwargs["data"]["token"] == "AT"
    text = tmp_config.read_text()
    assert "control-room" not in text
    assert "[acme]" in text
    assert "Logged out." in capsys.readouterr().out


@patch("canvas_cli.apps.auth.oauth.requests.post")
def test_logout_suppresses_revoke_network_error(mock_post: MagicMock, tmp_config: Path) -> None:
    """Test that Logout suppresses revoke network error."""
    tmp_config.write_text("[control-room]\naccess_token = AT\nrefresh_token = RT\nexpires_at = 1\n")
    mock_post.side_effect = requests.RequestException("boom")
    oauth.logout()  # should not raise
    assert "control-room" not in tmp_config.read_text()


def _trigger_callback(state: str, code: str = "auth_code_xyz", path: str | None = None) -> None:
    """Hit the local callback server until it accepts."""
    deadline = time_module.time() + 5
    p = path if path is not None else oauth.CALLBACK_PATH
    url = f"http://localhost:{oauth.CALLBACK_PORT}{p}?code={code}&state={state}"
    while time_module.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except urllib.error.HTTPError:
            return  # non-callback paths return 404 which still triggers handle_request
        except (urllib.error.URLError, ConnectionRefusedError, OSError):
            time_module.sleep(0.05)


@patch("canvas_cli.apps.auth.oauth.webbrowser.open")
@patch("canvas_cli.apps.auth.oauth.requests.post")
def test_login_happy_path(
    mock_post: MagicMock,
    mock_browser: MagicMock,
    tmp_config: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that Login happy path."""
    values = iter(["V" * 64, "FIXED_STATE"])
    monkeypatch.setattr(oauth.secrets, "token_urlsafe", lambda n: next(values))
    mock_post.return_value = _token_response(
        200, {"access_token": "AT", "refresh_token": "RT", "expires_in": 3600}
    )

    t = threading.Thread(target=_trigger_callback, args=("FIXED_STATE",))
    t.start()
    oauth.login()
    t.join()

    section = oauth._read_section()
    assert section["access_token"] == "AT"
    assert section["refresh_token"] == "RT"
    mock_browser.assert_called_once()
    authorize_url = mock_browser.call_args[0][0]
    assert "code_challenge=" in authorize_url
    assert "state=FIXED_STATE" in authorize_url


@patch("canvas_cli.apps.auth.oauth.webbrowser.open")
def test_login_no_auth_code_exits(
    mock_browser: MagicMock, tmp_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that Login no auth code exits."""
    values = iter(["V" * 64, "STATE_X"])
    monkeypatch.setattr(oauth.secrets, "token_urlsafe", lambda n: next(values))

    t = threading.Thread(target=_trigger_callback, args=("ignored",), kwargs={"path": "/wrong"})
    t.start()
    with pytest.raises(typer.Exit):
        oauth.login()
    t.join()


@patch("canvas_cli.apps.auth.oauth.webbrowser.open")
def test_login_state_mismatch_exits(
    mock_browser: MagicMock, tmp_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that Login state mismatch exits."""
    values = iter(["V" * 64, "EXPECTED_STATE"])
    monkeypatch.setattr(oauth.secrets, "token_urlsafe", lambda n: next(values))

    t = threading.Thread(target=_trigger_callback, args=("WRONG_STATE",))
    t.start()
    with pytest.raises(typer.Exit):
        oauth.login()
    t.join()


@patch("canvas_cli.apps.auth.oauth.webbrowser.open")
@patch("canvas_cli.apps.auth.oauth.requests.post")
def test_login_token_exchange_network_error_exits(
    mock_post: MagicMock,
    mock_browser: MagicMock,
    tmp_config: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that Login token exchange network error exits."""
    values = iter(["V" * 64, "S"])
    monkeypatch.setattr(oauth.secrets, "token_urlsafe", lambda n: next(values))
    mock_post.side_effect = requests.RequestException("boom")

    t = threading.Thread(target=_trigger_callback, args=("S",))
    t.start()
    with pytest.raises(typer.Exit):
        oauth.login()
    t.join()


@patch("canvas_cli.apps.auth.oauth.webbrowser.open")
@patch("canvas_cli.apps.auth.oauth.requests.post")
def test_login_token_exchange_non_200_exits(
    mock_post: MagicMock,
    mock_browser: MagicMock,
    tmp_config: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that Login token exchange non 200 exits."""
    values = iter(["V" * 64, "S"])
    monkeypatch.setattr(oauth.secrets, "token_urlsafe", lambda n: next(values))
    mock_post.return_value = _token_response(400, {"error": "invalid_grant"})

    t = threading.Thread(target=_trigger_callback, args=("S",))
    t.start()
    with pytest.raises(typer.Exit):
        oauth.login()
    t.join()
