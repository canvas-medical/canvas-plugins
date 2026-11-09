"""A Model Context Protocol server over the Agent Runner Framework's standard tools.

One SimpleAPI route, ``POST /mcp``, speaks MCP's JSON-RPC over the Streamable HTTP
transport, answering each request with plain JSON (the transport allows a server that
never streams). The server is stateless: no session id, no server-to-client requests.

An outside agent authenticates with ``Authorization: Bearer <MCP_API_KEY>``. The key is
practice-level trust, like any SimpleAPI key: calls act as Canvas Bot. What the key may
do is the ``MCP_TOOLS`` variable, a comma-separated list of tool names and ``@category``
groups: the practice's providers, open times, and configuration unless the operator lists
the patient tools, which search every patient, or a write. Patient searches are limited to
``PATIENT_SEARCHES_PER_MINUTE``.

A tool acts on one patient, the one the call names in ``patient_id``; this plugin checks
the patient exists and sets it as the call's patient, so a tool never takes a patient
from its other arguments. Write tools stage effects, which go back with the response and
are applied by Canvas like any SimpleAPI request's.
"""

import json
import time
from hmac import compare_digest
from http import HTTPStatus
from typing import Any
from uuid import uuid4

from canvas_sdk.agents import Capability, ToolNotAllowed, ToolRegistry, standard_tools
from canvas_sdk.caching.plugins import get_cache
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import BearerCredentials, SimpleAPI, api
from canvas_sdk.v1.data import Patient
from logger import log

PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26")
SERVER_INFO = {"name": "canvas-scheduling", "version": "0.0.1"}
KEY_VARIABLE = "MCP_API_KEY"
TOOLS_VARIABLE = "MCP_TOOLS"
# What a key may do unless the operator says otherwise: read the practice's providers,
# open times, and configuration. A key reaches patients only when MCP_TOOLS lists the
# patient tools, since find_patient searches every patient.
DEFAULT_TOOLS = (
    "@scheduling_reads",
    "find_practice_locations",
    "find_note_types",
    "find_reason_for_visit_codes",
)
# The most patient searches a key makes a minute: identifiers such as a birth date can be
# guessed, so a key cannot try them at speed.
PATIENT_SEARCHES_PER_MINUTE = 20
# Tools about the practice rather than one patient: they take no patient_id.
PRACTICE_CATEGORIES = frozenset({"config_reads", "scheduling_reads", "patient_search"})
PATIENT_ARGUMENT = {
    "type": "string",
    "description": (
        "The patient this call acts on: an id from find_patient. Required by every tool "
        "about a patient."
    ),
}

# JSON-RPC error codes.
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602


def _granted(secrets: dict[str, str]) -> ToolRegistry:
    """The tools the operator's MCP_TOOLS allows, or the read-only default."""
    listed = [name.strip() for name in str(secrets.get(TOOLS_VARIABLE) or "").split(",")]
    allowed = [name for name in listed if name] or list(DEFAULT_TOOLS)
    return standard_tools.scope(standard_tools.resolve_allowed(allowed))


def _over_search_limit() -> bool:
    """Claim one of this minute's patient-search slots; whether none was left.

    Each slot is claimed by storing this request's own token through ``get_or_set``, which
    the cache backend writes only when the slot is empty, so two concurrent requests never
    claim the same slot and the limit holds under a burst.
    """
    cache = get_cache()
    window = int(time.time() // 60)
    token = str(uuid4())
    for slot in range(PATIENT_SEARCHES_PER_MINUTE):
        key = f"mcp-patient-search-{window}-{slot}"
        if cache.get_or_set(key, token, timeout_seconds=120) == token:
            return False
    return True


def _about_a_patient(name: str) -> bool:
    return not PRACTICE_CATEGORIES & set(standard_tools.categories_for(name))


def _tool_list(registry: ToolRegistry) -> list[dict[str, Any]]:
    """The MCP tool descriptions: the registry's, with patient_id on the patient tools."""
    tools = []
    for definition in registry.definitions():
        schema = dict(definition["input_schema"])
        if _about_a_patient(definition["name"]):
            schema["properties"] = {**schema.get("properties", {}), "patient_id": PATIENT_ARGUMENT}
            schema["required"] = [*schema.get("required", []), "patient_id"]
        tools.append(
            {
                "name": definition["name"],
                "description": definition["description"],
                "inputSchema": schema,
            }
        )
    return tools


def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _tool_text(payload: Any, *, is_error: bool) -> dict[str, Any]:
    """A tools/call result: the tool's answer as JSON text, flagged when it failed."""
    text = payload if isinstance(payload, str) else json.dumps(payload, default=str)
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


class SchedulingMCP(SimpleAPI):
    """The MCP endpoint."""

    def authenticate(self, credentials: BearerCredentials) -> bool:
        """The bearer token is the plugin's MCP_API_KEY."""
        key = str(self.secrets.get(KEY_VARIABLE) or "")
        return bool(key) and compare_digest(credentials.token.encode(), key.encode())

    @api.post("/mcp")
    def mcp(self) -> list[Response | Effect]:
        """Answer one JSON-RPC message."""
        try:
            message = json.loads(self.request.body)
        except ValueError:
            return [JSONResponse(_error(None, PARSE_ERROR, "Parse error"))]
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return [JSONResponse(_error(None, INVALID_REQUEST, "Send one JSON-RPC 2.0 message"))]
        method = str(message.get("method") or "")
        if "id" not in message:
            # A notification, such as notifications/initialized: accepted, not answered.
            return [Response(status_code=HTTPStatus.ACCEPTED)]
        request_id = message["id"]
        params = message.get("params") or {}
        if not isinstance(params, dict):
            return [JSONResponse(_error(request_id, INVALID_PARAMS, "params must be an object"))]
        if method == "initialize":
            return [JSONResponse(_result(request_id, self._initialize(params)))]
        if method == "ping":
            return [JSONResponse(_result(request_id, {}))]
        if method == "tools/list":
            tools = _tool_list(_granted(self.secrets))
            return [JSONResponse(_result(request_id, {"tools": tools}))]
        if method == "tools/call":
            return self._call(request_id, params)
        return [JSONResponse(_error(request_id, METHOD_NOT_FOUND, f"Unknown method {method!r}"))]

    @api.get("/mcp")
    def mcp_stream(self) -> list[Response | Effect]:
        """This server never streams to the client."""
        return [Response(status_code=HTTPStatus.METHOD_NOT_ALLOWED)]

    def _initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Agree on a protocol version, and say the server offers tools."""
        asked = str(params.get("protocolVersion") or "")
        return {
            "protocolVersion": asked if asked in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
            "instructions": (
                "Canvas scheduling. Where the key may search patients, find the patient "
                "with find_patient, then pass its patient_id to the tools about a patient. "
                "Book only a time find_appointment_slots offered, and confirm it with the "
                "person first."
            ),
        }

    def _call(self, request_id: Any, params: dict[str, Any]) -> list[Response | Effect]:
        """Run one tool for the patient the call names; its effects go back with the answer."""
        name = str(params.get("name") or "")
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            return [JSONResponse(_error(request_id, INVALID_PARAMS, "arguments must be an object"))]
        arguments = dict(arguments)
        registry = _granted(self.secrets)
        schemas = {
            definition["name"]: definition["input_schema"] for definition in registry.definitions()
        }
        if name not in schemas:
            return [JSONResponse(_error(request_id, INVALID_PARAMS, f"Unknown tool {name!r}"))]
        patient_id = str(arguments.pop("patient_id", "") or "") or None
        missing = [key for key in schemas[name].get("required", []) if key not in arguments]
        if missing:
            answer = _tool_text(f"Missing required arguments: {', '.join(missing)}", is_error=True)
            return [JSONResponse(_result(request_id, answer))]
        if _about_a_patient(name) and not (
            patient_id and Patient.objects.filter(id=patient_id).exists()
        ):
            answer = _tool_text(
                "Pass the patient_id of a patient find_patient found.", is_error=True
            )
            return [JSONResponse(_result(request_id, answer))]
        if "patient_search" in standard_tools.categories_for(name) and _over_search_limit():
            answer = _tool_text(
                f"This key has reached its limit of {PATIENT_SEARCHES_PER_MINUTE} patient "
                "searches a minute; try again in a minute.",
                is_error=True,
            )
            return [JSONResponse(_result(request_id, answer))]
        # Patient search is the operator's grant: it is on only for a key MCP_TOOLS lets
        # call find_patient.
        searches = any(
            "patient_search" in standard_tools.categories_for(definition["name"])
            for definition in registry.definitions()
        )
        ctx: dict[str, Any] = {
            "patient_id": patient_id,
            "capabilities": frozenset({Capability.PATIENT_SEARCH}) if searches else frozenset(),
            "effects": [],
            "parent_tools": registry,
        }
        try:
            outcome = registry.execute(name, arguments, ctx=ctx)
        except (ValueError, ToolNotAllowed) as exc:
            # The tool saying what to pass differently, which the client's model needs.
            log.info(f"mcp tool={name} ok=0 reason={type(exc).__name__}")
            answer = _tool_text(f"Tool execution failed: {exc!s}", is_error=True)
            return [JSONResponse(_result(request_id, answer))]
        except Exception as exc:
            # Any other failure, such as a database error, stays on the server: its text
            # can describe the instance.
            log.info(f"mcp tool={name} ok=0 reason={type(exc).__name__}")
            answer = _tool_text("Tool execution failed.", is_error=True)
            return [JSONResponse(_result(request_id, answer))]
        effects: list[Effect] = list(ctx["effects"])
        log.info(f"mcp tool={name} ok=1 effects={len(effects)}")
        answer = _tool_text(outcome, is_error=False)
        if isinstance(outcome, dict):
            answer["structuredContent"] = outcome
        return [JSONResponse(_result(request_id, answer)), *effects]
