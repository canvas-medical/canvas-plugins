"""OAuth2 PKCE login/logout for Control Room."""

import base64
import contextlib
import hashlib
import http.server
import json
import secrets
import stat
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any

import requests
import typer

CREDENTIALS_DIR = Path.home() / ".canvas"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials"
CLIENT_ID = "canvas-cli"
CALLBACK_PORT = 9876
CALLBACK_PATH = "/callback"

# Default Control Room URL — overridable via --control-room flag
DEFAULT_CONTROL_ROOM_URL = "https://control-room.canvasmedical.com"


def _get_credentials() -> dict[str, str]:
    """Load stored credentials."""
    if not CREDENTIALS_FILE.exists():
        return {}
    return json.loads(CREDENTIALS_FILE.read_text())


def _save_credentials(data: dict[str, str]) -> None:
    """Save credentials with restricted permissions (0600)."""
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_FILE.write_text(json.dumps(data, indent=2))
    CREDENTIALS_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)


def _generate_pkce() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge (S256)."""
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


def get_access_token(control_room_url: str | None = None) -> str | None:
    """Get a valid access token, refreshing if needed."""
    creds = _get_credentials()
    return creds.get("access_token")


def refresh_access_token(control_room_url: str | None = None) -> str | None:
    """Refresh the access token using the stored refresh token."""
    creds = _get_credentials()
    cr_url = control_room_url or creds.get("control_room_url", DEFAULT_CONTROL_ROOM_URL)
    refresh_token = creds.get("refresh_token")

    if not refresh_token:
        return None

    try:
        resp = requests.post(
            f"{cr_url.rstrip('/')}/oauth/token/",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": CLIENT_ID,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            creds["access_token"] = data["access_token"]
            if "refresh_token" in data:
                creds["refresh_token"] = data["refresh_token"]
            _save_credentials(creds)
            return data["access_token"]
    except requests.RequestException:
        pass

    return None


def login(
    control_room_url: str = typer.Option(
        DEFAULT_CONTROL_ROOM_URL,
        "--control-room",
        help="Control Room URL",
    ),
) -> None:
    """Log in to Control Room via browser-based OAuth2."""
    code_verifier, code_challenge = _generate_pkce()
    state = secrets.token_urlsafe(32)

    # Capture the auth code via a local HTTP server
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
            pass  # Silence request logging

    server = http.server.HTTPServer(("localhost", CALLBACK_PORT), CallbackHandler)

    # Build the authorization URL
    authorize_url = f"{control_room_url.rstrip('/')}/oauth/authorize/?" + urllib.parse.urlencode(
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

    # Handle one request (the callback)
    server.handle_request()
    server.server_close()

    if not auth_code:
        print("Login failed: no authorization code received.")
        raise typer.Exit(1)

    if received_state != state:
        print("Login failed: state mismatch (possible CSRF attack).")
        raise typer.Exit(1)

    # Exchange auth code for tokens
    try:
        resp = requests.post(
            f"{control_room_url.rstrip('/')}/oauth/token/",
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

    tokens = resp.json()
    _save_credentials(
        {
            "control_room_url": control_room_url,
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token", ""),
        }
    )

    print(f"Logged in to {control_room_url}")
    print(f"Credentials saved to {CREDENTIALS_FILE}")


def logout() -> None:
    """Log out of Control Room and clear stored credentials."""
    creds = _get_credentials()
    cr_url = creds.get("control_room_url", DEFAULT_CONTROL_ROOM_URL)
    access_token = creds.get("access_token")

    # Try to revoke the token server-side
    if access_token:
        with contextlib.suppress(requests.RequestException):
            requests.post(
                f"{cr_url.rstrip('/')}/oauth/revoke_token/",
                data={"token": access_token, "client_id": CLIENT_ID},
                timeout=10,
            )

    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()
        print("Logged out. Credentials cleared.")
    else:
        print("No credentials found.")
