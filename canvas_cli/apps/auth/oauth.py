"""OAuth2 PKCE login/logout for Control Room."""

import base64
import configparser
import contextlib
import hashlib
import http.server
import secrets
import stat
import time
import urllib.parse
import webbrowser
from typing import Any

import requests
import typer

from canvas_cli.apps.auth.utils import CONFIG_PATH

CONTROL_ROOM_URL = "https://control-room.canvasmedical.com"
CONTROL_ROOM_SECTION = "control-room"
CLIENT_ID = "canvas-cli"
CALLBACK_PORT = 9876
CALLBACK_PATH = "/callback"
REFRESH_LEEWAY_SECONDS = 60


def _read_section() -> dict[str, str]:
    """Load the [control-room] section from credentials.ini."""
    if not CONFIG_PATH.exists():
        return {}
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if CONTROL_ROOM_SECTION not in config:
        return {}
    return dict(config[CONTROL_ROOM_SECTION])


def _replace_section(text: str, section: str, body: str | None) -> str:
    """Replace, append, or remove a section in INI text, preserving the rest verbatim.

    body=None removes the section. Otherwise, replaces in place if the section
    exists, else appends to the end of the file.
    """
    header = f"[{section}]"
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    found = False
    i = 0
    while i < len(lines):
        if lines[i].strip() == header:
            found = True
            i += 1
            while i < len(lines) and not lines[i].lstrip().startswith("["):
                i += 1
            if body is not None:
                out.append(body)
            continue
        out.append(lines[i])
        i += 1

    if not found and body is not None:
        if out and not out[-1].endswith("\n"):
            out.append("\n")
        if out:
            out.append("\n")
        out.append(body)

    return "".join(out)


def _write_section(data: dict[str, str | int]) -> None:
    """Write the [control-room] section, preserving the rest of credentials.ini."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    body = f"[{CONTROL_ROOM_SECTION}]\n" + "".join(f"{k} = {v}\n" for k, v in data.items())
    text = CONFIG_PATH.read_text() if CONFIG_PATH.exists() else ""
    CONFIG_PATH.write_text(_replace_section(text, CONTROL_ROOM_SECTION, body))
    CONFIG_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)


def _delete_section() -> None:
    """Remove the [control-room] section from credentials.ini, if present."""
    if not CONFIG_PATH.exists():
        return
    text = CONFIG_PATH.read_text()
    new_text = _replace_section(text, CONTROL_ROOM_SECTION, None)
    if new_text != text:
        CONFIG_PATH.write_text(new_text)
        CONFIG_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)


def _save_tokens(tokens: dict[str, Any]) -> None:
    """Persist tokens from an OAuth2 response into credentials.ini."""
    expires_at = int(time.time()) + int(tokens.get("expires_in") or 0)
    _write_section(
        {
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token", ""),
            "expires_at": expires_at,
        }
    )


def _generate_pkce() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge (S256)."""
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


def get_access_token() -> str | None:
    """Return a valid Control Room access token, refreshing proactively if near expiry."""
    creds = _read_section()
    access_token = creds.get("access_token")
    if not access_token:
        return None

    expires_at = int(creds.get("expires_at") or 0)
    if expires_at and expires_at - REFRESH_LEEWAY_SECONDS <= time.time():
        return refresh_access_token()

    return access_token


def refresh_access_token() -> str | None:
    """Refresh the access token using the stored refresh token."""
    creds = _read_section()
    refresh_token = creds.get("refresh_token")
    if not refresh_token:
        return None

    try:
        resp = requests.post(
            f"{CONTROL_ROOM_URL}/oauth/token/",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": CLIENT_ID,
            },
            timeout=30,
        )
    except requests.RequestException:
        return None

    if resp.status_code != 200:
        return None

    data = resp.json()
    _save_tokens(data)
    return data["access_token"]


def login() -> None:
    """Log in to Control Room via browser-based OAuth2."""
    code_verifier, code_challenge = _generate_pkce()
    state = secrets.token_urlsafe(32)

    auth_code: str | None = None
    received_state: str | None = None

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            nonlocal auth_code, received_state
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            if parsed.path == CALLBACK_PATH:
                auth_code = params.get("code", [None])[0]
                received_state = params.get("state", [None])[0]

                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h2>Login successful!</h2>"
                    b"<p>You can close this tab and return to the terminal.</p>"
                    b"</body></html>"
                )
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = http.server.HTTPServer(("localhost", CALLBACK_PORT), CallbackHandler)

    authorize_url = f"{CONTROL_ROOM_URL}/oauth/authorize/?" + urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": f"http://localhost:{CALLBACK_PORT}{CALLBACK_PATH}",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": state,
        }
    )

    print("Opening browser for login...")
    webbrowser.open(authorize_url)
    print(f"Waiting for callback on http://localhost:{CALLBACK_PORT}...")

    server.handle_request()
    server.server_close()

    if not auth_code:
        print("Login failed: no authorization code received.")
        raise typer.Exit(1)

    if received_state != state:
        print("Login failed: state mismatch (possible CSRF attack).")
        raise typer.Exit(1)

    try:
        resp = requests.post(
            f"{CONTROL_ROOM_URL}/oauth/token/",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": f"http://localhost:{CALLBACK_PORT}{CALLBACK_PATH}",
                "client_id": CLIENT_ID,
                "code_verifier": code_verifier,
            },
            timeout=30,
        )
    except requests.RequestException as e:
        print(f"Login failed: {e}")
        raise typer.Exit(1) from None

    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} {resp.text}")
        raise typer.Exit(1)

    _save_tokens(resp.json())

    print(f"Logged in to {CONTROL_ROOM_URL}")
    print(f"Credentials saved to {CONFIG_PATH} ([{CONTROL_ROOM_SECTION}])")


def logout() -> None:
    """Log out of Control Room and clear stored credentials."""
    creds = _read_section()
    access_token = creds.get("access_token")

    if access_token:
        with contextlib.suppress(requests.RequestException):
            requests.post(
                f"{CONTROL_ROOM_URL}/oauth/revoke_token/",
                data={"token": access_token, "client_id": CLIENT_ID},
                timeout=10,
            )

    if creds:
        _delete_section()
        print("Logged out. Credentials cleared.")
    else:
        print("No credentials found.")
