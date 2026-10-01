"""A small client for Canvas Platform's ``/api/v1/`` REST surface.

Every call carries the signed-in person's bearer token. An access token near its
expiry is refreshed before the call, and a ``401`` triggers one refresh and one
retry. A refusal raises ``PlatformError`` carrying the server's ``error``
sentence, which is written for the person reading it.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import click
import requests

from canvas_cli.apps.platform import auth

TIMEOUT_SECONDS = 30


class PlatformError(click.ClickException):
    """A refusal or transport failure from Canvas Platform."""

    def __init__(self, message: str, *, status: int | None = None, code: str = "") -> None:
        super().__init__(message)
        self.status = status
        self.code = code

    @classmethod
    def from_response(cls, response: requests.Response) -> PlatformError:
        """Build the error from a refusal, preferring the server's own sentence."""
        try:
            body = response.json()
        except ValueError:
            body = {}
        if not isinstance(body, dict):
            body = {}
        message = body.get("error") or f"Canvas Platform answered {response.status_code}."
        if field := body.get("field"):
            message = f"{message} (field: {field})"
        return cls(str(message), status=response.status_code, code=str(body.get("code") or ""))


def segment(value: str) -> str:
    """A path segment with everything but unreserved characters escaped."""
    return quote(value, safe="")


class PlatformClient:
    """Bearer-authenticated JSON calls against one platform origin."""

    def __init__(self, platform: str) -> None:
        self.platform = platform

    def _send(
        self, method: str, path: str, access_token: str, body: dict[str, Any] | None
    ) -> requests.Response:
        try:
            return requests.request(
                method,
                f"{self.platform}{path}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
                json=body,
                timeout=TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            raise PlatformError(
                f"Could not reach Canvas Platform at {self.platform}: {exc}"
            ) from exc

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        """Send one call and return its parsed JSON body (None for an empty one)."""
        tokens = auth.valid_tokens(self.platform)
        response = self._send(method, path, tokens["access_token"], body)
        if response.status_code == requests.codes.unauthorized:
            tokens = auth.refresh(self.platform, tokens["refresh_token"])
            response = self._send(method, path, tokens["access_token"], body)
            if response.status_code == requests.codes.unauthorized:
                raise auth.PlatformAuthError(
                    f"Canvas Platform at {self.platform} did not accept your session. "
                    "Run `canvas login` to sign in again."
                )
        if not response.ok:
            raise PlatformError.from_response(response)
        if not response.content:
            return None
        return response.json()

    def get(self, path: str) -> Any:
        """GET ``path``."""
        return self.request("GET", path)

    def post(self, path: str, body: dict[str, Any] | None = None) -> Any:
        """POST ``body`` to ``path``."""
        return self.request("POST", path, body)

    def put(self, path: str, body: dict[str, Any]) -> Any:
        """PUT ``body`` to ``path``."""
        return self.request("PUT", path, body)

    def delete(self, path: str) -> Any:
        """DELETE ``path``."""
        return self.request("DELETE", path)

    # -- the endpoints the CLI uses -------------------------------------------

    def me(self) -> dict[str, Any]:
        """``GET /api/v1/me``: the person and the organizations they belong to."""
        return self.get("/api/v1/me")

    def instances(self) -> list[dict[str, Any]]:
        """``GET /api/v1/instances``: what the person may reach and do on each."""
        return self.get("/api/v1/instances").get("instances", [])

    def plugin(self, name: str) -> dict[str, Any] | None:
        """``GET /api/v1/plugins/<name>``, or None when platform has no such plugin
        the person may see (platform answers 404 for both).
        """
        try:
            return self.get(f"/api/v1/plugins/{segment(name)}")
        except PlatformError as error:
            if error.status == requests.codes.not_found:
                return None
            raise

    def register_plugin(self, organization: str, name: str) -> dict[str, Any]:
        """``POST /api/v1/orgs/<org>/plugins``: create the plugin, or return it when it
        already belongs to ``organization``.
        """
        return self.post(f"/api/v1/orgs/{segment(organization)}/plugins", {"name": name})

    def git_credentials(self, name: str) -> dict[str, Any]:
        """``POST /api/v1/plugins/<name>/git-credentials``: a one-hour git token."""
        return self.post(f"/api/v1/plugins/{segment(name)}/git-credentials")

    def set_variable(
        self, instance: str, name: str, key: str, value: str, sensitive: bool | None
    ) -> Any:
        """``PUT`` one variable value on one instance."""
        body: dict[str, Any] = {"value": value}
        if sensitive is not None:
            body["sensitive"] = sensitive
        return self.put(self._variable_path(instance, name, key), body)

    def clear_variable(self, instance: str, name: str, key: str) -> Any:
        """``DELETE`` one variable value on one instance."""
        return self.delete(self._variable_path(instance, name, key))

    @staticmethod
    def _variable_path(instance: str, name: str, key: str) -> str:
        return (
            f"/api/v1/instances/{segment(instance)}/plugins/{segment(name)}"
            f"/variables/{segment(key)}"
        )

    def create_deployment(
        self, action: str, plugins: list[dict[str, str]], instances: list[str]
    ) -> dict[str, Any]:
        """``POST /api/v1/deployments``."""
        return self.post(
            "/api/v1/deployments",
            {"action": action, "plugins": plugins, "instances": instances},
        )

    def deployment(self, deployment_id: str) -> dict[str, Any]:
        """``GET /api/v1/deployments/<id>``."""
        return self.get(f"/api/v1/deployments/{segment(deployment_id)}")

    def answer_consent(self, request_id: int | str, approve: bool, reason: str = "") -> Any:
        """Approve or deny one consent request."""
        path = f"/api/v1/consent-requests/{segment(str(request_id))}"
        if approve:
            return self.post(f"{path}/approve")
        return self.post(f"{path}/deny", {"reason": reason} if reason else {})
