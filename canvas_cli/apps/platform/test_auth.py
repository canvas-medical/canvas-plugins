"""Tests for signing in to Canvas Platform: PKCE, the loopback flow, token storage and refresh."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import stat
import threading
import time
import urllib.request
from collections.abc import Callable
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import pytest
import requests
import requests_mock as requests_mock_module
from requests_mock.request import _RequestObjectProxy

from canvas_cli.apps.platform import auth

PLATFORM = "https://platform.example"


def _last(mock: requests_mock_module.Mocker) -> _RequestObjectProxy:
    """The most recent request the mock answered."""
    request = mock.last_request
    assert request is not None
    return request


def _token_response(n: int, expires_in: int = 3600) -> dict:
    return {
        "access_token": f"cnvs_ua_{n}",
        "refresh_token": f"cnvs_rt_{n}",
        "token_type": "Bearer",
        "expires_in": expires_in,
    }


# -- PKCE --------------------------------------------------------------------


def test_code_challenge_matches_rfc7636_appendix_b() -> None:
    """The S256 challenge for the RFC's own example verifier is the RFC's challenge."""
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    assert auth.code_challenge(verifier) == "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"


def test_code_verifier_is_random_and_within_rfc_bounds() -> None:
    """A verifier is 43 to 128 unreserved characters and differs every time."""
    first, second = auth.make_code_verifier(), auth.make_code_verifier()
    assert first != second
    assert 43 <= len(first) <= 128
    assert set(first) <= set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")
    digest = hashlib.sha256(first.encode()).digest()
    assert auth.code_challenge(first) == base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


# -- platform URL ------------------------------------------------------------


def test_resolve_platform_url_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """An explicit URL beats the environment, which beats the last login, which beats the default."""
    assert auth.resolve_platform_url() == auth.DEFAULT_PLATFORM_URL

    auth.save_tokens("https://platform-dev.example", _token_response(1), make_default=True)
    assert auth.resolve_platform_url() == "https://platform-dev.example"

    monkeypatch.setenv(auth.PLATFORM_URL_ENV, "env.example/some/path")
    assert auth.resolve_platform_url() == "https://env.example"

    assert auth.resolve_platform_url("http://127.0.0.1:8455/") == "http://127.0.0.1:8455"


# -- storage -----------------------------------------------------------------


def test_tokens_are_stored_per_platform_with_owner_only_permissions(
    isolate_platform_credentials: Path,
) -> None:
    """Each platform origin has its own token pair, in a file only its owner can read."""
    auth.save_tokens(PLATFORM, _token_response(1), make_default=True)
    auth.save_tokens("https://other.example", _token_response(2), make_default=False)

    mode = stat.S_IMODE(os.stat(isolate_platform_credentials).st_mode)
    assert mode == 0o600
    data = json.loads(isolate_platform_credentials.read_text())
    assert data["default"] == PLATFORM
    assert data["platforms"][PLATFORM]["refresh_token"] == "cnvs_rt_1"
    assert data["platforms"]["https://other.example"]["refresh_token"] == "cnvs_rt_2"

    auth.forget_tokens(PLATFORM)
    assert auth.stored_tokens(PLATFORM) is None
    assert auth.stored_tokens("https://other.example") is not None
    assert "default" not in json.loads(isolate_platform_credentials.read_text())


def test_valid_tokens_requires_a_session() -> None:
    """Without stored tokens, the person is told to run `canvas login`."""
    with pytest.raises(auth.PlatformAuthError, match="canvas login"):
        auth.valid_tokens(PLATFORM)


def test_valid_tokens_returns_unexpired_tokens_without_a_call(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """A token that is not near expiry is used as stored."""
    auth.save_tokens(PLATFORM, _token_response(1), make_default=True)
    assert auth.valid_tokens(PLATFORM)["access_token"] == "cnvs_ua_1"
    assert not requests_mock.called


def test_valid_tokens_refreshes_near_expiry_and_persists_the_rotated_pair(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """An access token inside the expiry margin is refreshed, and both new tokens are stored."""
    auth.save_tokens(PLATFORM, _token_response(1, expires_in=30), make_default=True)
    requests_mock.post(f"{PLATFORM}/oauth/token", json=_token_response(2))

    tokens = auth.valid_tokens(PLATFORM)

    assert tokens["access_token"] == "cnvs_ua_2"
    assert parse_qs(_last(requests_mock).text) == {
        "grant_type": ["refresh_token"],
        "refresh_token": ["cnvs_rt_1"],
        "client_id": ["canvas-cli"],
    }
    stored = auth.stored_tokens(PLATFORM)
    assert stored is not None
    assert stored["refresh_token"] == "cnvs_rt_2"


def test_refresh_uses_a_pair_another_process_already_rotated(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """When the stored refresh token differs from the one the caller saw, it is not spent again."""
    auth.save_tokens(PLATFORM, _token_response(2), make_default=True)

    tokens = auth.refresh(PLATFORM, "cnvs_rt_1")

    assert tokens["access_token"] == "cnvs_ua_2"
    assert not requests_mock.called


def test_refresh_invalid_grant_signs_out(requests_mock: requests_mock_module.Mocker) -> None:
    """An expired or revoked refresh token deletes the local session and asks for a login."""
    auth.save_tokens(PLATFORM, _token_response(1), make_default=True)
    requests_mock.post(f"{PLATFORM}/oauth/token", status_code=400, json={"error": "invalid_grant"})

    with pytest.raises(auth.PlatformAuthError, match="canvas login"):
        auth.refresh(PLATFORM, "cnvs_rt_1")
    assert auth.stored_tokens(PLATFORM) is None


def test_refresh_takes_over_a_stale_lock(
    requests_mock: requests_mock_module.Mocker, isolate_platform_credentials: Path
) -> None:
    """A lock file left by a process that died mid-refresh does not block forever."""
    auth.save_tokens(PLATFORM, _token_response(1), make_default=True)
    lock = isolate_platform_credentials.with_name(f"{isolate_platform_credentials.name}.lock")
    lock.touch()
    old = time.time() - auth.LOCK_STALE_SECONDS - 5
    os.utime(lock, (old, old))
    requests_mock.post(f"{PLATFORM}/oauth/token", json=_token_response(2))

    assert auth.refresh(PLATFORM, "cnvs_rt_1")["access_token"] == "cnvs_ua_2"
    assert not lock.exists()


# -- the browser flow --------------------------------------------------------


def _browser(
    params: dict[str, str] | None = None, *, state: str | None = None
) -> tuple[Callable[[str], bool], list[str]]:
    """A stand-in browser that follows the authorize URL straight to the redirect."""
    opened: list[str] = []

    def open_browser(url: str) -> bool:
        opened.append(url)
        query = parse_qs(urlparse(url).query)
        redirect = query["redirect_uri"][0]
        answer = {"state": state or query["state"][0], **(params or {"code": "the-code"})}

        def follow() -> None:
            with urllib.request.urlopen(f"{redirect}?{urlencode(answer)}", timeout=5) as page:
                page.read()

        threading.Thread(target=follow, daemon=True).start()
        return True

    return open_browser, opened


def test_login_exchanges_the_code_with_the_verifier(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """The authorize URL carries an S256 challenge, and the exchange proves it with the verifier."""
    requests_mock.post(f"{PLATFORM}/oauth/token", json=_token_response(1))
    open_browser, opened = _browser()
    printed: list[str] = []

    auth.login(PLATFORM, open_browser=open_browser, echo=printed.append, timeout_seconds=10)

    authorize = urlparse(opened[0])
    query = parse_qs(authorize.query)
    assert (
        f"{authorize.scheme}://{authorize.netloc}{authorize.path}" == f"{PLATFORM}/oauth/authorize"
    )
    assert query["response_type"] == ["code"]
    assert query["client_id"] == ["canvas-cli"]
    assert query["code_challenge_method"] == ["S256"]
    assert urlparse(query["redirect_uri"][0]).hostname == "127.0.0.1"
    assert any(opened[0] in line for line in printed)  # printed for headless use

    exchange = parse_qs(_last(requests_mock).text)
    assert exchange["grant_type"] == ["authorization_code"]
    assert exchange["code"] == ["the-code"]
    assert exchange["redirect_uri"] == query["redirect_uri"]
    assert auth.code_challenge(exchange["code_verifier"][0]) == query["code_challenge"][0]

    stored = auth.stored_tokens(PLATFORM)
    assert stored is not None
    assert stored["access_token"] == "cnvs_ua_1"
    assert auth.resolve_platform_url() == PLATFORM


def test_login_refuses_a_mismatched_state(requests_mock: requests_mock_module.Mocker) -> None:
    """A redirect whose state is not this attempt's is refused before any exchange."""
    open_browser, _ = _browser(state="forged")

    with pytest.raises(auth.PlatformAuthError, match="did not match"):
        auth.login(PLATFORM, open_browser=open_browser, echo=lambda _: None, timeout_seconds=10)
    assert not requests_mock.called
    assert auth.stored_tokens(PLATFORM) is None


def test_login_reports_a_declined_sign_in(requests_mock: requests_mock_module.Mocker) -> None:
    """`error=access_denied` says the sign-in was declined."""
    open_browser, _ = _browser({"error": "access_denied"})

    with pytest.raises(auth.PlatformAuthError, match="declined"):
        auth.login(PLATFORM, open_browser=open_browser, echo=lambda _: None, timeout_seconds=10)
    assert not requests_mock.called


def test_login_times_out_without_a_redirect() -> None:
    """A browser that never comes back ends the wait with a sentence, not a hang."""
    with pytest.raises(auth.PlatformAuthError, match="did not finish"):
        auth.login(PLATFORM, open_browser=lambda _: True, echo=lambda _: None, timeout_seconds=0.1)


def test_login_reports_a_refused_code(requests_mock: requests_mock_module.Mocker) -> None:
    """A code platform will not exchange names the OAuth error."""
    requests_mock.post(f"{PLATFORM}/oauth/token", status_code=400, json={"error": "invalid_grant"})
    open_browser, _ = _browser()

    with pytest.raises(auth.PlatformAuthError, match="invalid_grant"):
        auth.login(PLATFORM, open_browser=open_browser, echo=lambda _: None, timeout_seconds=10)


# -- logout ------------------------------------------------------------------


def test_logout_revokes_the_refresh_token_and_deletes_it(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """Logout posts the refresh token to /oauth/revoke and forgets the session."""
    auth.save_tokens(PLATFORM, _token_response(1), make_default=True)
    requests_mock.post(f"{PLATFORM}/oauth/revoke", status_code=200)

    assert auth.logout(PLATFORM) == ""
    assert parse_qs(_last(requests_mock).text) == {
        "token": ["cnvs_rt_1"],
        "client_id": ["canvas-cli"],
    }
    assert auth.stored_tokens(PLATFORM) is None


def test_logout_forgets_tokens_even_when_platform_is_unreachable(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """A failed revocation is reported, and the local session is deleted anyway."""
    auth.save_tokens(PLATFORM, _token_response(1), make_default=True)
    requests_mock.post(f"{PLATFORM}/oauth/revoke", exc=requests.exceptions.ConnectionError("down"))

    problem = auth.logout(PLATFORM)
    assert problem and "could not reach" in problem
    assert auth.stored_tokens(PLATFORM) is None


def test_logout_without_a_session() -> None:
    """Logging out when signed out says so."""
    assert auth.logout(PLATFORM) is None
