"""Signing in to Canvas Platform from the command line.

``canvas login`` runs the OAuth 2.0 authorization-code flow with PKCE (RFC 7636,
``S256``) against platform. The browser finishes the sign-in, platform redirects
to a one-shot listener on a loopback port, and the code is exchanged for an
access token and a rotating refresh token.

Tokens are stored per platform origin in ``~/.canvas/platform-credentials.json``
with ``0600`` permissions, apart from ``credentials.ini`` (which the developer
writes by hand, and which a rewrite would strip of comments) and ``tokens.json``
(a cache of instance tokens that is written with default permissions). The file
also records which platform the last ``canvas login`` signed in to, so a session
against a non-default platform keeps being used without repeating ``--platform``.
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
import json
import os
import secrets
import time
import webbrowser
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import click
import requests

CLIENT_ID = "canvas-cli"
DEFAULT_PLATFORM_URL = "https://platform.canvasmedical.com"
PLATFORM_URL_ENV = "CANVAS_PLATFORM_URL"
# A service account's token, which CI sets in place of signing in. It is used as it
# is: there is nothing to refresh, and a person rotates it on Platform's Credentials
# page.
SERVICE_TOKEN_ENV = "CANVAS_PLATFORM_TOKEN"
CREDENTIALS_PATH = Path.home() / ".canvas" / "platform-credentials.json"

# Refresh this many seconds before the access token's stated expiry, so a token
# that is valid when read does not expire in flight.
EXPIRY_MARGIN_SECONDS = 60
LOGIN_TIMEOUT_SECONDS = 300
TIMEOUT_SECONDS = 30

# A refresh holds a lock file beside the credentials, because a deploy and the
# git credential helper it spawns can both find the access token expired at
# once, and spending the same rotating refresh token twice fails the second.
LOCK_WAIT_SECONDS = 15.0
LOCK_STALE_SECONDS = 30.0


class PlatformAuthError(click.ClickException):
    """A sign-in problem the person fixes by running ``canvas login``."""


def not_signed_in(platform: str) -> PlatformAuthError:
    """The refusal for a command that needs a platform session and has none."""
    return PlatformAuthError(
        f"You are not signed in to Canvas Platform at {platform}. Run `canvas login` first."
    )


# -- platform URL ------------------------------------------------------------


def normalize_platform_url(url: str) -> str:
    """``scheme://host[:port]`` for a platform URL, defaulting the scheme to https."""
    if "://" not in url:
        url = f"https://{url}"
    parsed = urlparse(url)
    if not parsed.netloc:
        raise click.BadParameter(f"'{url}' is not a platform URL")
    return f"{parsed.scheme}://{parsed.netloc}"


def platform_url_source(explicit: str | None = None) -> tuple[str, str]:
    """The platform to talk to, and a phrase naming where that choice came from.

    In order: an explicit ``--platform``, ``CANVAS_PLATFORM_URL``, the platform
    the last ``canvas login`` signed in to, and https://platform.canvasmedical.com.
    """
    if explicit:
        return normalize_platform_url(explicit), "--platform"
    if from_env := os.environ.get(PLATFORM_URL_ENV):
        return normalize_platform_url(from_env), PLATFORM_URL_ENV
    if last := _load().get("default"):
        return normalize_platform_url(last), "your last `canvas login`"
    return DEFAULT_PLATFORM_URL, "the default"


def resolve_platform_url(explicit: str | None = None) -> str:
    """The platform to talk to, chosen as ``platform_url_source`` describes."""
    return platform_url_source(explicit)[0]


# -- token storage -----------------------------------------------------------


def _load() -> dict[str, Any]:
    if not CREDENTIALS_PATH.exists():
        return {}
    try:
        return json.loads(CREDENTIALS_PATH.read_text())
    except ValueError as exc:
        raise PlatformAuthError(
            f"{CREDENTIALS_PATH} is not valid JSON ({exc}). Move it aside and run `canvas login`."
        ) from exc


def _save(data: dict[str, Any]) -> None:
    """Write the credentials file atomically, readable by its owner only."""
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = CREDENTIALS_PATH.with_name(f".{CREDENTIALS_PATH.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as file:
        json.dump(data, file, indent=2)
    os.chmod(temporary, 0o600)
    os.replace(temporary, CREDENTIALS_PATH)


def service_token() -> str | None:
    """The service account token CI set in ``CANVAS_PLATFORM_TOKEN``, if any."""
    return os.environ.get(SERVICE_TOKEN_ENV, "").strip() or None


def stored_session(platform: str) -> dict[str, Any] | None:
    """The ``canvas login`` session stored for a platform origin, whatever the environment says."""
    return _load().get("platforms", {}).get(platform)


def stored_tokens(platform: str) -> dict[str, Any] | None:
    """The token set for a platform origin, or None when signed out.

    A service account token in the environment wins over a stored sign-in, so a CI
    runner acts as its service account whatever a previous ``canvas login`` left.
    """
    if token := service_token():
        return {"access_token": token, "service": True}
    return stored_session(platform)


def save_tokens(platform: str, token_response: dict[str, Any], *, make_default: bool) -> None:
    """Persist the token pair a ``/oauth/token`` call returned."""
    data = _load()
    data.setdefault("platforms", {})[platform] = {
        "access_token": token_response["access_token"],
        "refresh_token": token_response["refresh_token"],
        "expires_at": int(time.time()) + int(token_response["expires_in"]),
    }
    if make_default:
        data["default"] = platform
    _save(data)


def forget_tokens(platform: str) -> None:
    """Delete a platform's tokens, and its default status, from local storage."""
    data = _load()
    data.get("platforms", {}).pop(platform, None)
    if data.get("default") == platform:
        data.pop("default")
    _save(data)


@contextlib.contextmanager
def _refresh_lock() -> Iterator[None]:
    """An exclusive lock file, portable across operating systems.

    A lock older than ``LOCK_STALE_SECONDS`` belongs to a process that died
    mid-refresh, since a refresh is a single HTTP call, and is taken over.
    """
    lock = CREDENTIALS_PATH.with_name(f"{CREDENTIALS_PATH.name}.lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + LOCK_WAIT_SECONDS
    while True:
        try:
            os.close(os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600))
            break
        except FileExistsError:
            with contextlib.suppress(FileNotFoundError):
                if time.time() - lock.stat().st_mtime > LOCK_STALE_SECONDS:
                    lock.unlink()
                    continue
            if time.monotonic() > deadline:
                raise PlatformAuthError(
                    f"Timed out waiting for {lock}. If no other canvas command is running, "
                    "delete it and try again."
                ) from None
            time.sleep(0.1)
    try:
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            lock.unlink()


def _token_request(platform: str, form: dict[str, str]) -> requests.Response:
    try:
        return requests.post(f"{platform}/oauth/token", data=form, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise PlatformAuthError(f"Could not reach Canvas Platform at {platform}: {exc}") from exc


def _oauth_error(response: requests.Response) -> str:
    try:
        return str(response.json().get("error") or response.status_code)
    except ValueError:
        return str(response.status_code)


def refresh(platform: str, stale_refresh_token: str) -> dict[str, Any]:
    """Exchange a refresh token for a new pair, persist it, and return it.

    ``stale_refresh_token`` is the refresh token the caller last saw. When
    another process has rotated it in the meantime, its fresh pair is returned
    rather than spending the rotated-out token, which platform would refuse.
    """
    with _refresh_lock():
        current = stored_tokens(platform)
        if current is None:
            raise not_signed_in(platform)
        if current["refresh_token"] != stale_refresh_token and not _expired(current):
            return current

        response = _token_request(
            platform,
            {
                "grant_type": "refresh_token",
                "refresh_token": current["refresh_token"],
                "client_id": CLIENT_ID,
            },
        )
        if response.status_code != requests.codes.ok:
            error = _oauth_error(response)
            if error == "invalid_grant":
                forget_tokens(platform)
                raise PlatformAuthError(
                    f"Your Canvas Platform session at {platform} has ended. "
                    "Run `canvas login` to sign in again."
                )
            raise PlatformAuthError(f"Could not refresh your Canvas Platform session: {error}")

        save_tokens(platform, response.json(), make_default=False)
        refreshed = stored_tokens(platform)
        assert refreshed is not None
        return refreshed


def _expired(tokens: dict[str, Any]) -> bool:
    return int(tokens["expires_at"]) - EXPIRY_MARGIN_SECONDS <= time.time()


def valid_tokens(platform: str) -> dict[str, Any]:
    """The platform's token set, refreshed first when the access token is about to expire."""
    tokens = stored_tokens(platform)
    if tokens is None:
        raise not_signed_in(platform)
    if tokens.get("service"):
        return tokens
    if _expired(tokens):
        return refresh(platform, tokens["refresh_token"])
    return tokens


# -- the authorization-code flow ---------------------------------------------


def make_code_verifier() -> str:
    """A random PKCE ``code_verifier``: 86 characters from the unreserved set."""
    return secrets.token_urlsafe(64)


def code_challenge(verifier: str) -> str:
    """The ``S256`` challenge: unpadded base64url of the verifier's SHA-256."""
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


@dataclass
class _Callback:
    """What the browser's redirect to the loopback listener carried."""

    code: str | None = None
    state: str | None = None
    error: str | None = None
    received: bool = False


_CLOSE_PAGE = (
    b"<!doctype html><html><head><meta charset='utf-8'><title>Canvas CLI</title></head>"
    b"<body style='font-family: sans-serif; margin: 3rem'>"
    b"<p>%s</p><p>You can close this tab and return to your terminal.</p></body></html>"
)


def _listener(callback: _Callback) -> HTTPServer:
    """A loopback HTTP server on a random port that records one ``/callback`` hit."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return
            query = parse_qs(parsed.query)
            callback.code = query.get("code", [None])[0]
            callback.state = query.get("state", [None])[0]
            callback.error = query.get("error", [None])[0]
            callback.received = True
            message = (
                b"Signed in to Canvas Platform." if callback.code else b"Sign-in did not complete."
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(_CLOSE_PAGE % message)

        def log_message(self, format: str, *args: Any) -> None:
            """Keep the request log out of the terminal."""

    return HTTPServer(("127.0.0.1", 0), Handler)


def authorization_url(platform: str, redirect_uri: str, challenge: str, state: str) -> str:
    """The ``/oauth/authorize`` URL the browser opens."""
    query = urlencode(
        {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": redirect_uri,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": state,
        }
    )
    return f"{platform}/oauth/authorize?{query}"


def login(
    platform: str,
    *,
    open_browser: Callable[[str], bool] = webbrowser.open,
    echo: Callable[[str], None] = click.echo,
    timeout_seconds: float = LOGIN_TIMEOUT_SECONDS,
) -> None:
    """Sign in through the browser and store the resulting tokens for ``platform``."""
    verifier = make_code_verifier()
    state = secrets.token_urlsafe(32)
    callback = _Callback()
    server = _listener(callback)
    try:
        redirect_uri = f"http://127.0.0.1:{server.server_address[1]}/callback"
        url = authorization_url(platform, redirect_uri, code_challenge(verifier), state)
        echo("Opening your browser to sign in to Canvas Platform. If it does not open, visit:")
        echo(f"  {url}")
        open_browser(url)

        deadline = time.monotonic() + timeout_seconds
        while not callback.received and (remaining := deadline - time.monotonic()) > 0:
            server.timeout = min(1.0, remaining)
            server.handle_request()
    finally:
        server.server_close()

    if not callback.received:
        raise PlatformAuthError(
            f"Sign-in did not finish within {int(timeout_seconds)} seconds. Run `canvas login` again."
        )
    if callback.state != state:
        raise PlatformAuthError(
            "The sign-in response did not match this login attempt, so it was refused. "
            "Run `canvas login` again."
        )
    if callback.error:
        reason = (
            "was declined" if callback.error == "access_denied" else f"failed ({callback.error})"
        )
        raise PlatformAuthError(f"Sign-in {reason} in the browser.")
    if not callback.code:
        raise PlatformAuthError("The sign-in response carried no authorization code.")

    response = _token_request(
        platform,
        {
            "grant_type": "authorization_code",
            "code": callback.code,
            "redirect_uri": redirect_uri,
            "client_id": CLIENT_ID,
            "code_verifier": verifier,
        },
    )
    if response.status_code != requests.codes.ok:
        raise PlatformAuthError(
            f"Canvas Platform refused the sign-in code: {_oauth_error(response)}. "
            "Run `canvas login` again."
        )
    save_tokens(platform, response.json(), make_default=True)


def logout(platform: str) -> str | None:
    """Revoke the platform session and delete its local tokens.

    Returns None when there was no session, or an error sentence when platform
    could not revoke it. The local tokens are deleted either way, since keeping
    them would leave the person signed in on this machine after asking not to be.
    A service account token in ``CANVAS_PLATFORM_TOKEN`` is not a session: it is
    rotated or revoked on Platform's Credentials page, so logout leaves it alone.
    """
    tokens = stored_session(platform)
    if tokens is None:
        return None
    try:
        response = requests.post(
            f"{platform}/oauth/revoke",
            data={"token": tokens["refresh_token"], "client_id": CLIENT_ID},
            timeout=TIMEOUT_SECONDS,
        )
        problem = "" if response.ok else f"platform answered {response.status_code}"
    except requests.RequestException as exc:
        problem = f"could not reach {platform}: {exc}"
    forget_tokens(platform)
    return problem
