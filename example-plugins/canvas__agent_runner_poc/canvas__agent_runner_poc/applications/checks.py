"""Checks on what a chat request sends, so a malformed one gets a 400 rather than a 500."""

from http import HTTPStatus
from json import JSONDecodeError
from typing import Any
from uuid import UUID

from canvas_sdk.effects.simple_api import JSONResponse

# The longest message a person may send in one turn.
MAX_MESSAGE_CHARS = 10_000
# The longest reason a person may give for a decision.
MAX_REASON_CHARS = 2_000
DECISIONS = ("approve", "deny")


class BadRequest(Exception):
    """A request the chat cannot act on, with the reason the response gives."""

    def response(self) -> JSONResponse:
        """The 400 that names what was wrong with the request."""
        return JSONResponse({"error": str(self)}, status_code=HTTPStatus.BAD_REQUEST)


def body(request: Any) -> dict[str, Any]:
    """The request's JSON object."""
    try:
        value = request.json()
    except (JSONDecodeError, UnicodeDecodeError):
        raise BadRequest("The body is not JSON.") from None
    if not isinstance(value, dict):
        raise BadRequest("The body is not a JSON object.")
    return value


def uuid(value: Any, name: str) -> str:
    """``value``, which must be a UUID string, as sent."""
    if not isinstance(value, str):
        raise BadRequest(f"`{name}` must be a UUID.")
    try:
        UUID(value)
    except ValueError:
        raise BadRequest(f"`{name}` must be a UUID.") from None
    return value


def query_uuid(request: Any, name: str) -> str:
    """The query parameter ``name``, which must be a UUID."""
    return uuid(request.query_params.get(name), name)


def text(value: Any, name: str, max_chars: int) -> str:
    """``value``, which must be text that is not blank and at most ``max_chars`` long."""
    if not isinstance(value, str) or not value.strip():
        raise BadRequest(f"`{name}` must be text.")
    if len(value) > max_chars:
        raise BadRequest(f"`{name}` is longer than {max_chars} characters.")
    return value


def decision(payload: dict[str, Any]) -> tuple[str, str, str]:
    """The proposal id, decision, and reason a decide request sends."""
    proposal_id = uuid(payload.get("proposal_id"), "proposal_id")
    choice = payload.get("decision")
    if choice not in DECISIONS:
        raise BadRequest("`decision` must be 'approve' or 'deny'.")
    reason = payload.get("reason") or ""
    if reason:
        reason = text(reason, "reason", MAX_REASON_CHARS)
    return proposal_id, choice, reason
