"""Tests for the MCP handler base class, decorators, and authorize machinery."""

import json

import pytest

from canvas_sdk.effects import Effect
from canvas_sdk.effects.mcp import (
    MCPCallToolResponse,
    MCPGetPromptResponse,
    MCPReadResourceResponse,
    ResourceContent,
    TextContent,
)
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.mcp import MCP, prompt, resource, tool
from canvas_sdk.handlers.mcp.authorize import (
    all_of,
    any_authenticated,
    any_of,
    has_role,
    has_scope,
)


def _make_event(event_type: EventType, **context: object) -> Event:
    """Build an MCP event with the given context dict."""
    return Event(
        event_request=EventRequest(
            type=event_type,
            target=None,
            context=json.dumps(context, separators=(",", ":")),
            target_type=None,
        )
    )


# ---------------------------------------------------------------------------
# Sample handlers
# ---------------------------------------------------------------------------


class _AlwaysAllowMCP(MCP):
    @tool(
        name="open_tool",
        description="open",
        input_schema={"type": "object"},
        authorize=any_authenticated,
    )
    def open_tool(self, arguments: dict) -> MCPCallToolResponse:
        return MCPCallToolResponse(content=[TextContent(text="opened")])

    @tool(
        name="biller_tool",
        description="biller",
        input_schema={"type": "object"},
        authorize=has_role("biller"),
    )
    def biller_tool(self, arguments: dict) -> MCPCallToolResponse:
        return MCPCallToolResponse(content=[TextContent(text="charged")])


class _MissingAuthMCP(MCP):
    @tool(
        name="forgot_authorize",
        description="oops",
        input_schema={"type": "object"},
    )
    def forgot_authorize(self, arguments: dict) -> MCPCallToolResponse:
        return MCPCallToolResponse(content=[TextContent(text="should not be reached")])


class _ResourcePromptMCP(MCP):
    @resource(
        uri="readme",
        name="readme",
        description="r",
        mime_type="text/plain",
        authorize=any_authenticated,
    )
    def readme(self) -> MCPReadResourceResponse:
        return MCPReadResourceResponse(
            contents=[ResourceContent(uri="readme", mime_type="text/plain", text="hi")]
        )

    @prompt(
        name="greet",
        description="g",
        arguments=[],
        authorize=any_authenticated,
    )
    def greet(self, arguments: dict) -> MCPGetPromptResponse:
        return MCPGetPromptResponse(description="g", messages=[])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_decorator_registers_tool() -> None:
    """The @tool decorator records metadata on the method and the class collects it."""
    assert "open_tool" in _AlwaysAllowMCP._TOOLS
    assert "biller_tool" in _AlwaysAllowMCP._TOOLS
    reg = _AlwaysAllowMCP._TOOLS["open_tool"]
    assert reg.description == "open"
    assert reg.authorize is any_authenticated


def test_list_tools_filters_by_authorize() -> None:
    """tools/list shows only entries the actor passes; biller_tool hidden for non-billers."""
    event = _make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={})
    handler = _AlwaysAllowMCP(event=event)
    [effect] = handler.compute()
    payload = json.loads(effect.payload)
    names = sorted(t["name"] for t in payload["tools"])
    # biller_tool's authorize calls event_actor_has_role("biller"), which returns False here
    # because no Staff/Patient is resolvable in this test scope.
    assert names == ["open_tool"]


def test_call_authorized_tool_invokes_method() -> None:
    """An authorized tool call dispatches to the decorated method."""
    event = _make_event(
        EventType.MCP_CALL_TOOL, actor="42", headers={}, name="open_tool", arguments={}
    )
    handler = _AlwaysAllowMCP(event=event)
    [effect] = handler.compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is False
    assert payload["content"][0]["text"] == "opened"


def test_call_unauthorized_tool_returns_minus_32001() -> None:
    """Calling a tool whose authorize predicate returns False yields -32001."""
    event = _make_event(
        EventType.MCP_CALL_TOOL, actor="42", headers={}, name="biller_tool", arguments={}
    )
    handler = _AlwaysAllowMCP(event=event)
    [effect] = handler.compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32001


def test_missing_authorize_lists_with_prefix() -> None:
    """A tool decorated without authorize= still appears in tools/list, prefixed."""
    event = _make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={})
    handler = _MissingAuthMCP(event=event)
    [effect] = handler.compute()
    payload = json.loads(effect.payload)
    assert len(payload["tools"]) == 1
    assert payload["tools"][0]["description"].startswith("[unconfigured authorization]")


def test_missing_authorize_call_returns_specific_error() -> None:
    """Calling a tool with no authorize= returns -32001 with an actionable message."""
    event = _make_event(
        EventType.MCP_CALL_TOOL,
        actor="42",
        headers={},
        name="forgot_authorize",
        arguments={},
    )
    handler = _MissingAuthMCP(event=event)
    [effect] = handler.compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32001
    assert "no authorization policy was specified" in payload["error"]["message"]
    assert "@tool" in payload["error"]["message"]


def test_accept_event_for_targeted_call() -> None:
    """accept_event() is True only for events whose targeted name is registered here."""
    open_event = _make_event(
        EventType.MCP_CALL_TOOL, actor="42", headers={}, name="open_tool", arguments={}
    )
    assert _AlwaysAllowMCP(event=open_event).accept_event() is True

    missing_event = _make_event(
        EventType.MCP_CALL_TOOL, actor="42", headers={}, name="not_registered", arguments={}
    )
    assert _AlwaysAllowMCP(event=missing_event).accept_event() is False


def test_accept_event_for_list_events() -> None:
    """List events always accept (filtering happens via authorize=)."""
    event = _make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={})
    assert _AlwaysAllowMCP(event=event).accept_event() is True


def test_resource_and_prompt_round_trip() -> None:
    """resources/read and prompts/get dispatch to the right method."""
    rev = _make_event(
        EventType.MCP_READ_RESOURCE, actor="42", headers={}, plugin_name="x", uri="readme"
    )
    handler = _ResourcePromptMCP(event=rev)
    [effect] = handler.compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is False
    assert payload["contents"][0]["text"] == "hi"

    pev = _make_event(EventType.MCP_GET_PROMPT, actor="42", headers={}, name="greet", arguments={})
    handler = _ResourcePromptMCP(event=pev)
    [effect] = handler.compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is False
    assert payload["description"] == "g"


def test_event_actor_property() -> None:
    """event_actor reads from context['actor']."""
    event = _make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={})
    handler = _AlwaysAllowMCP(event=event)
    assert handler.event_actor == "42"


def test_has_scope_helper() -> None:
    """has_scope reads `x-oauth-scopes` header content."""
    event = _make_event(
        EventType.MCP_LIST_TOOLS,
        actor="42",
        headers={"x-oauth-scopes": "read:patient write:billing"},
    )
    handler = _AlwaysAllowMCP(event=event)
    assert handler.event_actor_has_scope("read:patient") is True
    assert handler.event_actor_has_scope("nope") is False


def test_all_of_predicate() -> None:
    """all_of requires every component predicate to pass."""
    pred = all_of(any_authenticated, has_scope("read:patient"))
    event = _make_event(
        EventType.MCP_LIST_TOOLS,
        actor="42",
        headers={"x-oauth-scopes": "read:patient"},
    )
    handler = _AlwaysAllowMCP(event=event)
    assert pred(handler) is True
    event_no_scope = _make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={})
    handler_no_scope = _AlwaysAllowMCP(event=event_no_scope)
    assert pred(handler_no_scope) is False


def test_any_of_predicate() -> None:
    """any_of passes if any component predicate passes."""
    pred = any_of(has_scope("missing"), any_authenticated)
    event = _make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={})
    handler = _AlwaysAllowMCP(event=event)
    assert pred(handler) is True


def test_authorize_exception_fails_closed() -> None:
    """If a predicate raises, the SDK denies and continues running other entries."""

    def boom(handler: MCP) -> bool:
        raise RuntimeError("db down")

    class _ExplodingMCP(MCP):
        @tool(
            name="ok",
            description="o",
            input_schema={"type": "object"},
            authorize=any_authenticated,
        )
        def ok(self, arguments: dict) -> MCPCallToolResponse:
            return MCPCallToolResponse(content=[TextContent(text="ok")])

        @tool(
            name="broken",
            description="b",
            input_schema={"type": "object"},
            authorize=boom,
        )
        def broken(self, arguments: dict) -> MCPCallToolResponse:
            return MCPCallToolResponse(content=[TextContent(text="should not run")])

    event = _make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={})
    handler = _ExplodingMCP(event=event)
    [effect] = handler.compute()
    payload = json.loads(effect.payload)
    names = [t["name"] for t in payload["tools"]]
    # `broken` is filtered out because its predicate raised.
    assert names == ["ok"]

    call_event = _make_event(
        EventType.MCP_CALL_TOOL,
        actor="42",
        headers={},
        name="broken",
        arguments={},
    )
    [effect] = _ExplodingMCP(event=call_event).compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32001


def test_responds_to_includes_all_mcp_events() -> None:
    """RESPONDS_TO covers all six MCP_* event types so the runner registers them."""
    expected = {
        EventType.Name(EventType.MCP_LIST_TOOLS),
        EventType.Name(EventType.MCP_LIST_RESOURCES),
        EventType.Name(EventType.MCP_LIST_PROMPTS),
        EventType.Name(EventType.MCP_CALL_TOOL),
        EventType.Name(EventType.MCP_READ_RESOURCE),
        EventType.Name(EventType.MCP_GET_PROMPT),
    }
    assert set(MCP.RESPONDS_TO) == expected


# ---------------------------------------------------------------------------
# Resource and prompt code paths (mirror tool tests)
# ---------------------------------------------------------------------------


class _MissingAuthResourcePromptMCP(MCP):
    @resource(
        uri="naked",
        name="naked",
        description="resource with no authorize=",
        mime_type="text/plain",
    )
    def naked(self) -> MCPReadResourceResponse:
        return MCPReadResourceResponse(
            contents=[ResourceContent(uri="naked", mime_type="text/plain", text="x")]
        )

    @prompt(name="silent", description="prompt with no authorize=", arguments=[])
    def silent(self, arguments: dict) -> MCPGetPromptResponse:
        return MCPGetPromptResponse(description="d", messages=[])


def test_resource_missing_authorize_listed_with_prefix() -> None:
    """A resource without authorize= still appears in resources/list, prefixed."""
    event = _make_event(EventType.MCP_LIST_RESOURCES, actor="42", headers={})
    [effect] = _MissingAuthResourcePromptMCP(event=event).compute()
    payload = json.loads(effect.payload)
    assert payload["resources"][0]["description"].startswith("[unconfigured authorization]")


def test_resource_missing_authorize_call_returns_specific_error() -> None:
    """resources/read on a no-authorize entry returns -32001 with actionable message."""
    event = _make_event(
        EventType.MCP_READ_RESOURCE, actor="42", headers={}, plugin_name="x", uri="naked"
    )
    [effect] = _MissingAuthResourcePromptMCP(event=event).compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32001
    assert "@resource" in payload["error"]["message"]


def test_prompt_missing_authorize_listed_with_prefix() -> None:
    """A prompt without authorize= still appears in prompts/list, prefixed."""
    event = _make_event(EventType.MCP_LIST_PROMPTS, actor="42", headers={})
    [effect] = _MissingAuthResourcePromptMCP(event=event).compute()
    payload = json.loads(effect.payload)
    assert payload["prompts"][0]["description"].startswith("[unconfigured authorization]")


def test_prompt_missing_authorize_call_returns_specific_error() -> None:
    """prompts/get on a no-authorize entry returns -32001 with actionable message."""
    event = _make_event(
        EventType.MCP_GET_PROMPT, actor="42", headers={}, name="silent", arguments={}
    )
    [effect] = _MissingAuthResourcePromptMCP(event=event).compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32001
    assert "@prompt" in payload["error"]["message"]


class _DenyResourcePromptMCP(MCP):
    @resource(
        uri="locked",
        name="locked",
        description="r",
        mime_type="text/plain",
        authorize=has_role("biller"),
    )
    def locked(self) -> MCPReadResourceResponse:
        return MCPReadResourceResponse(
            contents=[ResourceContent(uri="locked", mime_type="text/plain", text="x")]
        )

    @prompt(name="locked_prompt", description="p", arguments=[], authorize=has_role("biller"))
    def locked_prompt(self, arguments: dict) -> MCPGetPromptResponse:
        return MCPGetPromptResponse(description="d", messages=[])


def test_resource_unauthorized_returns_minus_32001() -> None:
    """resources/read where authorize denies → -32001."""
    event = _make_event(
        EventType.MCP_READ_RESOURCE, actor="42", headers={}, plugin_name="x", uri="locked"
    )
    [effect] = _DenyResourcePromptMCP(event=event).compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32001


def test_prompt_unauthorized_returns_minus_32001() -> None:
    """prompts/get where authorize denies → -32001."""
    event = _make_event(
        EventType.MCP_GET_PROMPT, actor="42", headers={}, name="locked_prompt", arguments={}
    )
    [effect] = _DenyResourcePromptMCP(event=event).compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32001


# ---------------------------------------------------------------------------
# Method-raised exception paths (mapped to -32603)
# ---------------------------------------------------------------------------


class _RaisingMCP(MCP):
    @tool(
        name="boom_tool",
        description="t",
        input_schema={"type": "object"},
        authorize=any_authenticated,
    )
    def boom_tool(self, arguments: dict) -> MCPCallToolResponse:
        raise RuntimeError("tool exploded")

    @resource(
        uri="boom_resource",
        name="r",
        description="r",
        mime_type="text/plain",
        authorize=any_authenticated,
    )
    def boom_resource(self) -> MCPReadResourceResponse:
        raise RuntimeError("resource exploded")

    @prompt(name="boom_prompt", description="p", arguments=[], authorize=any_authenticated)
    def boom_prompt(self, arguments: dict) -> MCPGetPromptResponse:
        raise RuntimeError("prompt exploded")


def test_tool_method_exception_maps_to_minus_32603() -> None:
    """A tool method that raises produces is_error=True with code -32603."""
    event = _make_event(
        EventType.MCP_CALL_TOOL,
        actor="42",
        headers={},
        name="boom_tool",
        arguments={},
    )
    [effect] = _RaisingMCP(event=event).compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32603
    assert "tool exploded" in payload["error"]["message"]


def test_resource_method_exception_maps_to_minus_32603() -> None:
    """A resource method that raises produces is_error=True with code -32603."""
    event = _make_event(
        EventType.MCP_READ_RESOURCE,
        actor="42",
        headers={},
        plugin_name="x",
        uri="boom_resource",
    )
    [effect] = _RaisingMCP(event=event).compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32603


def test_prompt_method_exception_maps_to_minus_32603() -> None:
    """A prompt method that raises produces is_error=True with code -32603."""
    event = _make_event(
        EventType.MCP_GET_PROMPT,
        actor="42",
        headers={},
        name="boom_prompt",
        arguments={},
    )
    [effect] = _RaisingMCP(event=event).compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32603


# ---------------------------------------------------------------------------
# accept_event corners
# ---------------------------------------------------------------------------


def test_accept_event_for_resource_event() -> None:
    """accept_event True only when the requested URI is registered for resource events."""
    handler_known = _ResourcePromptMCP(
        event=_make_event(
            EventType.MCP_READ_RESOURCE,
            actor="42",
            headers={},
            plugin_name="x",
            uri="readme",
        )
    )
    assert handler_known.accept_event() is True
    handler_unknown = _ResourcePromptMCP(
        event=_make_event(
            EventType.MCP_READ_RESOURCE,
            actor="42",
            headers={},
            plugin_name="x",
            uri="missing",
        )
    )
    assert handler_unknown.accept_event() is False


def test_accept_event_for_prompt_event() -> None:
    """accept_event True only when the requested name is registered for prompt events."""
    handler_known = _ResourcePromptMCP(
        event=_make_event(
            EventType.MCP_GET_PROMPT, actor="42", headers={}, name="greet", arguments={}
        )
    )
    assert handler_known.accept_event() is True
    handler_unknown = _ResourcePromptMCP(
        event=_make_event(
            EventType.MCP_GET_PROMPT, actor="42", headers={}, name="missing", arguments={}
        )
    )
    assert handler_unknown.accept_event() is False


def test_accept_event_rejects_unknown_event_type() -> None:
    """accept_event returns False for event types not in the MCP set (defensive)."""
    handler = _AlwaysAllowMCP(
        event=_make_event(EventType.SIMPLE_API_REQUEST, actor="42", headers={})
    )
    assert handler.accept_event() is False


# ---------------------------------------------------------------------------
# event_actor_* helpers
# ---------------------------------------------------------------------------


def test_event_actor_has_scope_list_value() -> None:
    """event_actor_has_scope accepts a list of scopes in the header for clients that pass JSON."""
    event = _make_event(
        EventType.MCP_LIST_TOOLS,
        actor="42",
        headers={"x-oauth-scopes": ["read:patient", "write:billing"]},
    )
    handler = _AlwaysAllowMCP(event=event)
    assert handler.event_actor_has_scope("read:patient") is True
    assert handler.event_actor_has_scope("nope") is False


def test_event_actor_has_scope_unsupported_value_returns_false() -> None:
    """A non-string, non-list scopes header returns False (defensive)."""
    event = _make_event(
        EventType.MCP_LIST_TOOLS,
        actor="42",
        headers={"x-oauth-scopes": 42},
    )
    handler = _AlwaysAllowMCP(event=event)
    assert handler.event_actor_has_scope("anything") is False


def test_event_actor_user_returns_none_without_canvas_logged_in_user_headers() -> None:
    """When the trusted canvas-logged-in-user-* headers aren't set, the helper returns None."""
    handler = _AlwaysAllowMCP(event=_make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={}))
    assert handler.event_actor_user is None


def test_event_actor_has_role_without_user_returns_false() -> None:
    """Without a resolvable Staff/Patient user, has_role returns False."""
    handler = _AlwaysAllowMCP(event=_make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={}))
    assert handler.event_actor_has_role("anything") is False


def test_event_actor_anonymous_returns_none() -> None:
    """event_actor returns None when actor is missing/empty."""
    event = _make_event(EventType.MCP_LIST_TOOLS, headers={})  # no `actor`
    assert _AlwaysAllowMCP(event=event).event_actor is None


# ---------------------------------------------------------------------------
# List filtering via denying authorize (skipped entry path)
# ---------------------------------------------------------------------------


def test_resource_list_skips_denied_entries() -> None:
    """resources/list filters out entries whose authorize predicate denies."""
    event = _make_event(EventType.MCP_LIST_RESOURCES, actor="42", headers={})
    [effect] = _DenyResourcePromptMCP(event=event).compute()
    payload = json.loads(effect.payload)
    # `locked` requires has_role('biller'); without a resolvable Staff user the predicate
    # returns False, so the entry is filtered out.
    assert payload["resources"] == []


def test_prompt_list_skips_denied_entries() -> None:
    """prompts/list filters out entries whose authorize predicate denies."""
    event = _make_event(EventType.MCP_LIST_PROMPTS, actor="42", headers={})
    [effect] = _DenyResourcePromptMCP(event=event).compute()
    payload = json.loads(effect.payload)
    assert payload["prompts"] == []


# ---------------------------------------------------------------------------
# compute() outer try/except defensive path
# ---------------------------------------------------------------------------


def test_compute_with_unsupported_event_type_returns_internal_error() -> None:
    """If somehow an unsupported event type reaches compute(), the catch-all returns -32603."""
    handler = _AlwaysAllowMCP(
        event=_make_event(EventType.SIMPLE_API_REQUEST, actor="42", headers={})
    )
    [effect] = handler.compute()
    payload = json.loads(effect.payload)
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32603


def test_authorization_sentinel_callable_denies() -> None:
    """Direct call on _AuthorizationNotSpecified always returns False."""
    from canvas_sdk.handlers.mcp.mcp import _AUTH_NOT_SPECIFIED

    handler = _AlwaysAllowMCP(event=_make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={}))
    assert _AUTH_NOT_SPECIFIED(handler) is False


def test_event_actor_user_resolves_via_canvas_logged_in_user_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When canvas-logged-in-user-* headers are set, the helper queries Staff/Patient by key."""

    class _StubStaff:
        @staticmethod
        def filter(**_kwargs: object) -> object:
            class _QS:
                def first(self) -> str:
                    return "staff-stub"

            return _QS()

    class _StubPatient:
        @staticmethod
        def filter(**_kwargs: object) -> object:
            class _QS:
                def first(self) -> str:
                    return "patient-stub"

            return _QS()

    import canvas_sdk.v1.data as v1
    import canvas_sdk.v1.data.patient as patient_mod

    monkeypatch.setattr(v1, "Staff", type("Staff", (), {"objects": _StubStaff()}))
    monkeypatch.setattr(patient_mod, "Patient", type("Patient", (), {"objects": _StubPatient()}))

    staff_handler = _AlwaysAllowMCP(
        event=_make_event(
            EventType.MCP_LIST_TOOLS,
            actor="42",
            headers={
                "canvas-logged-in-user-type": "Staff",
                "canvas-logged-in-user-id": "abc",
            },
        )
    )
    assert staff_handler.event_actor_user == "staff-stub"

    patient_handler = _AlwaysAllowMCP(
        event=_make_event(
            EventType.MCP_LIST_TOOLS,
            actor="42",
            headers={
                "canvas-logged-in-user-type": "Patient",
                "canvas-logged-in-user-id": "xyz",
            },
        )
    )
    assert patient_handler.event_actor_user == "patient-stub"


def test_event_actor_has_role_consults_user_roles(monkeypatch: pytest.MonkeyPatch) -> None:
    """has_role queries the resolved user's roles relation."""

    class _Roles:
        def __init__(self, names: set[str]) -> None:
            self._names = names

        def filter(self, name: str) -> object:
            class _QS:
                def __init__(self, hit: bool) -> None:
                    self._hit = hit

                def exists(self) -> bool:
                    return self._hit

            return _QS(name in self._names)

    class _UserWithRoles:
        roles: _Roles = _Roles({"biller"})

    handler = _AlwaysAllowMCP(event=_make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={}))
    monkeypatch.setattr(type(handler), "event_actor_user", property(lambda self: _UserWithRoles()))
    assert handler.event_actor_has_role("biller") is True
    assert handler.event_actor_has_role("admin") is False


def test_compute_with_unsupported_list_event_returns_empty() -> None:
    """A list event whose dispatch raises returns [] (so other plugins still aggregate)."""

    class _BrokenListMCP(MCP):
        @tool(
            name="t",
            description="d",
            input_schema={"type": "object"},
            authorize=any_authenticated,
        )
        def t(self, arguments: dict) -> MCPCallToolResponse:
            return MCPCallToolResponse(content=[TextContent(text="ok")])

        def _list_tools(self) -> Effect:  # noqa: D401
            raise RuntimeError("forced failure")

    handler = _BrokenListMCP(event=_make_event(EventType.MCP_LIST_TOOLS, actor="42", headers={}))
    # Returns [] (list events swallow exceptions so other plugins' contributions can aggregate).
    assert handler.compute() == []
