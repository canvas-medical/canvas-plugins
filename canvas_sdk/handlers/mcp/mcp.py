from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ClassVar

import sentry_sdk

from canvas_sdk.effects import Effect
from canvas_sdk.effects.mcp import (
    MCPCallToolResponse,
    MCPGetPromptResponse,
    MCPPromptsListResponse,
    MCPReadResourceResponse,
    MCPResourcesListResponse,
    MCPToolsListResponse,
)
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from logger import log


class _AuthorizationNotSpecified:
    """Sentinel predicate. Always denies. Detected by the SDK to produce a discoverable error
    message at call time so developers see what's wrong without having to tail class-load logs.
    """

    def __call__(self, handler: "MCP") -> bool:
        # Defensive: in normal flow we detect this sentinel by isinstance and never invoke it,
        # but if a caller plumbs it through as a regular predicate we must still deny.
        return False


_AUTH_NOT_SPECIFIED = _AuthorizationNotSpecified()

Predicate = Callable[["MCP"], bool]


@dataclass
class _ToolRegistration:
    name: str
    description: str
    input_schema: dict[str, Any]
    method: Callable[..., MCPCallToolResponse]
    authorize: Predicate


@dataclass
class _ResourceRegistration:
    uri: str
    name: str
    description: str
    mime_type: str
    method: Callable[..., MCPReadResourceResponse]
    authorize: Predicate


@dataclass
class _PromptRegistration:
    name: str
    description: str
    arguments: list[dict[str, Any]]
    method: Callable[..., MCPGetPromptResponse]
    authorize: Predicate


def tool(
    *,
    name: str,
    description: str,
    input_schema: dict[str, Any],
    authorize: Predicate | _AuthorizationNotSpecified = _AUTH_NOT_SPECIFIED,
) -> Callable[[Callable[..., MCPCallToolResponse]], Callable[..., MCPCallToolResponse]]:
    """Decorator marking an `MCP` subclass method as an MCP tool.

    `authorize=` is required in spirit, but missing it does not raise — the SDK fails closed at
    call time with a specific actionable error message so developers without log-streaming see
    the problem on first invocation. Class-load logs a warning naming the offending tool.
    """

    def deco(
        fn: Callable[..., MCPCallToolResponse],
    ) -> Callable[..., MCPCallToolResponse]:
        if isinstance(authorize, _AuthorizationNotSpecified):
            log.warning(
                f"@tool {name!r} on {fn.__module__}.{fn.__qualname__} is missing authorize=; "
                f"the tool will deny all callers until set."
            )
        fn._mcp_tool = {  # type: ignore[attr-defined]
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "authorize": authorize,
        }
        return fn

    return deco


def resource(
    *,
    uri: str,
    name: str,
    description: str,
    mime_type: str = "text/plain",
    authorize: Predicate | _AuthorizationNotSpecified = _AUTH_NOT_SPECIFIED,
) -> Callable[[Callable[..., MCPReadResourceResponse]], Callable[..., MCPReadResourceResponse]]:
    """Decorator marking an `MCP` subclass method as an MCP resource.

    See `tool` for the rationale on the missing-`authorize` behavior.
    """

    def deco(
        fn: Callable[..., MCPReadResourceResponse],
    ) -> Callable[..., MCPReadResourceResponse]:
        if isinstance(authorize, _AuthorizationNotSpecified):
            log.warning(
                f"@resource {uri!r} on {fn.__module__}.{fn.__qualname__} is missing authorize=; "
                f"the resource will deny all callers until set."
            )
        fn._mcp_resource = {  # type: ignore[attr-defined]
            "uri": uri,
            "name": name,
            "description": description,
            "mime_type": mime_type,
            "authorize": authorize,
        }
        return fn

    return deco


def prompt(
    *,
    name: str,
    description: str,
    arguments: list[dict[str, Any]] | None = None,
    authorize: Predicate | _AuthorizationNotSpecified = _AUTH_NOT_SPECIFIED,
) -> Callable[[Callable[..., MCPGetPromptResponse]], Callable[..., MCPGetPromptResponse]]:
    """Decorator marking an `MCP` subclass method as an MCP prompt.

    See `tool` for the rationale on the missing-`authorize` behavior.
    """

    def deco(
        fn: Callable[..., MCPGetPromptResponse],
    ) -> Callable[..., MCPGetPromptResponse]:
        if isinstance(authorize, _AuthorizationNotSpecified):
            log.warning(
                f"@prompt {name!r} on {fn.__module__}.{fn.__qualname__} is missing authorize=; "
                f"the prompt will deny all callers until set."
            )
        fn._mcp_prompt = {  # type: ignore[attr-defined]
            "name": name,
            "description": description,
            "arguments": list(arguments or []),
            "authorize": authorize,
        }
        return fn

    return deco


_LIST_EVENT_TYPES = (
    EventType.MCP_LIST_TOOLS,
    EventType.MCP_LIST_RESOURCES,
    EventType.MCP_LIST_PROMPTS,
)


_UNAUTHORIZED_ERROR = {"code": -32001, "message": "Unauthorized"}


def _missing_authorize_error(kind: str, name: str) -> dict[str, Any]:
    return {
        "code": -32001,
        "message": (
            f"{kind.capitalize()} '{name}' is denied because no authorization policy was "
            f"specified. Add authorize=<predicate> to the @{kind} decorator."
        ),
    }


class MCP(BaseHandler):
    """Base class for plugins that expose MCP tools, resources, and prompts.

    Subclass and decorate methods with `@tool`, `@resource`, or `@prompt`. Each decorator takes a
    required `authorize=` callable that gates both list visibility and call execution. By the
    time a predicate runs, `event_actor` is guaranteed non-null (the platform rejects anonymous
    requests before reaching the runner).
    """

    RESPONDS_TO = [
        EventType.Name(EventType.MCP_LIST_TOOLS),
        EventType.Name(EventType.MCP_LIST_RESOURCES),
        EventType.Name(EventType.MCP_LIST_PROMPTS),
        EventType.Name(EventType.MCP_CALL_TOOL),
        EventType.Name(EventType.MCP_READ_RESOURCE),
        EventType.Name(EventType.MCP_GET_PROMPT),
    ]

    _TOOLS: ClassVar[dict[str, _ToolRegistration]]
    _RESOURCES: ClassVar[dict[str, _ResourceRegistration]]
    _PROMPTS: ClassVar[dict[str, _PromptRegistration]]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._TOOLS = {}
        cls._RESOURCES = {}
        cls._PROMPTS = {}
        for attr in cls.__dict__.values():
            if not callable(attr):
                continue
            if meta := getattr(attr, "_mcp_tool", None):
                cls._TOOLS[meta["name"]] = _ToolRegistration(
                    name=meta["name"],
                    description=meta["description"],
                    input_schema=meta["input_schema"],
                    method=attr,
                    authorize=meta["authorize"],
                )
            elif meta := getattr(attr, "_mcp_resource", None):
                cls._RESOURCES[meta["uri"]] = _ResourceRegistration(
                    uri=meta["uri"],
                    name=meta["name"],
                    description=meta["description"],
                    mime_type=meta["mime_type"],
                    method=attr,
                    authorize=meta["authorize"],
                )
            elif meta := getattr(attr, "_mcp_prompt", None):
                cls._PROMPTS[meta["name"]] = _PromptRegistration(
                    name=meta["name"],
                    description=meta["description"],
                    arguments=meta["arguments"],
                    method=attr,
                    authorize=meta["authorize"],
                )

    @property
    def _ctx(self) -> dict[str, Any]:
        return self.event.context

    @property
    def event_actor(self) -> str | None:
        """The id of the actor making the request, or None for anonymous (unreachable in v1
        because the view blocks anonymous before emission, but kept nullable for safety).
        """
        actor = self._ctx.get("actor")
        return str(actor) if actor else None

    @property
    def event_actor_user(self) -> Any:
        """Return the resolved Staff or Patient model, or None.

        Lookup is deferred to home-app via the `canvas-logged-in-user-*` headers if present, or
        falls back to looking up by `event_actor` id. Returning Any rather than a typed model
        avoids a SDK→home-app circular dependency; plugins can branch on type as needed.
        """
        from canvas_sdk.v1.data import Staff  # local import to keep top-level light
        from canvas_sdk.v1.data.patient import Patient

        headers = self._ctx.get("headers") or {}
        kind = headers.get("canvas-logged-in-user-type")
        key = headers.get("canvas-logged-in-user-id")
        # home-app stamps the model's external `key` value into this header (see SimpleAPIView's
        # actor-resolution path); on the SDK side, `Staff`/`Patient` expose that as `id`.
        if kind == "Staff" and key:
            return Staff.objects.filter(id=key).first()
        if kind == "Patient" and key:
            return Patient.objects.filter(id=key).first()
        return None

    def event_actor_has_role(self, role: str) -> bool:
        """Return True if the actor has the named role.

        Default implementation checks the resolved Staff user's roles; plugins may override for
        custom RBAC schemes.
        """
        user = self.event_actor_user
        if user is None or not hasattr(user, "roles"):
            return False
        return user.roles.filter(name=role).exists()

    def event_actor_has_scope(self, scope: str) -> bool:
        """Return True if the OAuth token used by the request includes the given scope.

        Reads scope claims from the `authorization` header context if present.
        """
        headers = self._ctx.get("headers") or {}
        scopes = headers.get("x-oauth-scopes", "")
        if isinstance(scopes, str):
            return scope in scopes.split()
        if isinstance(scopes, (list, tuple)):
            return scope in scopes
        return False

    def accept_event(self) -> bool:
        """List events: always accept; SDK filters entries via per-entry authorize=.
        Targeted events (call/read/get): accept only if the bare name is registered here.
        """
        evt = self.event.type
        if evt in _LIST_EVENT_TYPES:
            return True
        ctx = self._ctx
        if evt == EventType.MCP_CALL_TOOL:
            return ctx.get("name") in self._TOOLS
        if evt == EventType.MCP_READ_RESOURCE:
            return ctx.get("uri") in self._RESOURCES
        if evt == EventType.MCP_GET_PROMPT:
            return ctx.get("name") in self._PROMPTS
        return False

    def compute(self) -> list[Effect]:
        """Dispatch the MCP event to the matching internal handler and produce effects."""
        try:
            evt = self.event.type
            if evt == EventType.MCP_LIST_TOOLS:
                return [self._list_tools()]
            if evt == EventType.MCP_LIST_RESOURCES:
                return [self._list_resources()]
            if evt == EventType.MCP_LIST_PROMPTS:
                return [self._list_prompts()]
            if evt == EventType.MCP_CALL_TOOL:
                return [self._call_tool()]
            if evt == EventType.MCP_READ_RESOURCE:
                return [self._read_resource()]
            if evt == EventType.MCP_GET_PROMPT:
                return [self._get_prompt()]
            raise AssertionError(f"Cannot handle event type {EventType.Name(evt)}")
        except Exception as exception:
            log.exception(f"Error handling '{EventType.Name(self.event.type)}' event")
            sentry_sdk.capture_exception(exception)
            # Targeted events surface the failure to the client; list events get an empty list
            # so other plugins' contributions still aggregate.
            if self.event.type in _LIST_EVENT_TYPES:
                return []
            return [
                MCPCallToolResponse(
                    is_error=True, error={"code": -32603, "message": "Internal error"}
                ).apply()
            ]

    def _safe_authorize(self, predicate: Predicate, kind: str, name: str) -> bool:
        """Run an authorize predicate. Predicate exceptions fail closed and are logged."""
        try:
            return bool(predicate(self))
        except Exception as exception:  # pragma: no cover - defensive
            log.exception(f"authorize predicate raised for {kind} {name!r}; treating as denied")
            sentry_sdk.capture_exception(exception)
            return False

    def _list_tools(self) -> Effect:
        tools: list[dict[str, Any]] = []
        for reg in self._TOOLS.values():
            description = reg.description
            if isinstance(reg.authorize, _AuthorizationNotSpecified):
                # Listed even when unauthorized so devs see the broken state in mcp-inspector.
                description = f"[unconfigured authorization] {description}"
            elif not self._safe_authorize(reg.authorize, "tool", reg.name):
                continue
            tools.append(
                {
                    "name": reg.name,
                    "description": description,
                    "inputSchema": reg.input_schema,
                }
            )
        return MCPToolsListResponse(tools=tools).apply()

    def _list_resources(self) -> Effect:
        resources: list[dict[str, Any]] = []
        for reg in self._RESOURCES.values():
            description = reg.description
            if isinstance(reg.authorize, _AuthorizationNotSpecified):
                description = f"[unconfigured authorization] {description}"
            elif not self._safe_authorize(reg.authorize, "resource", reg.uri):
                continue
            resources.append(
                {
                    "uri": reg.uri,
                    "name": reg.name,
                    "description": description,
                    "mimeType": reg.mime_type,
                }
            )
        return MCPResourcesListResponse(resources=resources).apply()

    def _list_prompts(self) -> Effect:
        prompts: list[dict[str, Any]] = []
        for reg in self._PROMPTS.values():
            description = reg.description
            if isinstance(reg.authorize, _AuthorizationNotSpecified):
                description = f"[unconfigured authorization] {description}"
            elif not self._safe_authorize(reg.authorize, "prompt", reg.name):
                continue
            prompts.append(
                {
                    "name": reg.name,
                    "description": description,
                    "arguments": reg.arguments,
                }
            )
        return MCPPromptsListResponse(prompts=prompts).apply()

    def _call_tool(self) -> Effect:
        ctx = self._ctx
        name = ctx.get("name", "")
        reg = self._TOOLS[name]
        if isinstance(reg.authorize, _AuthorizationNotSpecified):
            return MCPCallToolResponse(
                is_error=True, error=_missing_authorize_error("tool", name)
            ).apply()
        if not self._safe_authorize(reg.authorize, "tool", name):
            return MCPCallToolResponse(is_error=True, error=_UNAUTHORIZED_ERROR).apply()
        try:
            result = reg.method(self, ctx.get("arguments") or {})
        except Exception as exception:
            log.exception(f"Tool {name!r} raised")
            sentry_sdk.capture_exception(exception)
            return MCPCallToolResponse(
                is_error=True,
                error={"code": -32603, "message": str(exception) or "Internal error"},
            ).apply()
        return result.apply()

    def _read_resource(self) -> Effect:
        ctx = self._ctx
        uri = ctx.get("uri", "")
        reg = self._RESOURCES[uri]
        if isinstance(reg.authorize, _AuthorizationNotSpecified):
            return MCPReadResourceResponse(
                is_error=True, error=_missing_authorize_error("resource", uri)
            ).apply()
        if not self._safe_authorize(reg.authorize, "resource", uri):
            return MCPReadResourceResponse(is_error=True, error=_UNAUTHORIZED_ERROR).apply()
        try:
            result = reg.method(self)
        except Exception as exception:
            log.exception(f"Resource {uri!r} raised")
            sentry_sdk.capture_exception(exception)
            return MCPReadResourceResponse(
                is_error=True,
                error={"code": -32603, "message": str(exception) or "Internal error"},
            ).apply()
        return result.apply()

    def _get_prompt(self) -> Effect:
        ctx = self._ctx
        name = ctx.get("name", "")
        reg = self._PROMPTS[name]
        if isinstance(reg.authorize, _AuthorizationNotSpecified):
            return MCPGetPromptResponse(
                is_error=True, error=_missing_authorize_error("prompt", name)
            ).apply()
        if not self._safe_authorize(reg.authorize, "prompt", name):
            return MCPGetPromptResponse(is_error=True, error=_UNAUTHORIZED_ERROR).apply()
        try:
            result = reg.method(self, ctx.get("arguments") or {})
        except Exception as exception:
            log.exception(f"Prompt {name!r} raised")
            sentry_sdk.capture_exception(exception)
            return MCPGetPromptResponse(
                is_error=True,
                error={"code": -32603, "message": str(exception) or "Internal error"},
            ).apply()
        return result.apply()


__exports__ = ("MCP", "tool", "resource", "prompt")
