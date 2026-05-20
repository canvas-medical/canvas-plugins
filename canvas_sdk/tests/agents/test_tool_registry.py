from typing import Any

import pytest

from canvas_sdk.agents import ToolNotAllowed, ToolRegistry


def _passthrough(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Echo back what was passed in — a useful test executor."""
    return {"args": arguments, "ctx": ctx}


def test_registry_starts_empty() -> None:
    """A fresh registry has no definitions and no executors."""
    registry = ToolRegistry()
    assert registry.definitions() == []


def test_register_adds_definition_and_executor() -> None:
    """A registered tool shows up in definitions() and executes via execute()."""
    registry = ToolRegistry()
    registry.register(
        {"name": "echo", "description": "echo", "input_schema": {"type": "object"}},
        _passthrough,
    )
    assert [d["name"] for d in registry.definitions()] == ["echo"]
    result = registry.execute("echo", {"hello": "world"}, ctx={"k": "v"})
    assert result == {"args": {"hello": "world"}, "ctx": {"k": "v"}}


def test_register_rejects_definition_without_name() -> None:
    """A definition missing the 'name' key is a programmer error, not a runtime case."""
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="missing a 'name' key"):
        registry.register({"description": "no name here"}, _passthrough)


def test_register_rejects_duplicate_name() -> None:
    """Two tools cannot share a name in the same registry."""
    registry = ToolRegistry()
    registry.register(
        {"name": "echo", "description": "first", "input_schema": {"type": "object"}},
        _passthrough,
    )
    with pytest.raises(ValueError, match="already registered"):
        registry.register(
            {"name": "echo", "description": "second", "input_schema": {"type": "object"}},
            _passthrough,
        )


def test_tool_decorator_registers_with_executor() -> None:
    """The @registry.tool decorator pairs the definition with the decorated function."""
    registry = ToolRegistry()

    @registry.tool(name="ping", description="ping", input_schema={"type": "object"})
    def _ping(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> str:
        return "pong"

    assert [d["name"] for d in registry.definitions()] == ["ping"]
    assert registry.execute("ping", {}, ctx={}) == "pong"


def test_extend_copies_tools_from_other_registry() -> None:
    """extend() copies definitions and executor refs; later mutations don't leak."""
    source = ToolRegistry()

    @source.tool(name="a", description="a", input_schema={"type": "object"})
    def _a(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> str:
        return "a"

    target = ToolRegistry()
    target.extend(source)

    @target.tool(name="b", description="b", input_schema={"type": "object"})
    def _b(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> str:
        return "b"

    # Target has both; source still has only its own tool.
    assert sorted(d["name"] for d in target.definitions()) == ["a", "b"]
    assert [d["name"] for d in source.definitions()] == ["a"]


def test_extend_raises_on_name_collision() -> None:
    """extend() into a registry that already has the same tool name is a hard error."""
    source = ToolRegistry()
    source.register(
        {"name": "dup", "description": "from source", "input_schema": {"type": "object"}},
        _passthrough,
    )
    target = ToolRegistry()
    target.register(
        {"name": "dup", "description": "from target", "input_schema": {"type": "object"}},
        _passthrough,
    )

    with pytest.raises(ValueError, match="already registered"):
        target.extend(source)


def test_execute_unknown_tool_raises() -> None:
    """Asking for a tool that wasn't registered is a clean ValueError.

    The agent loop catches this and reports back as ``tool_result`` with
    ``is_error=True``, so the model self-corrects.
    """
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="Unknown tool"):
        registry.execute("nonexistent", {}, ctx={})


def test_definitions_returns_a_copy() -> None:
    """definitions() must not return the internal list (callers might mutate it)."""
    registry = ToolRegistry()
    registry.register(
        {"name": "t", "description": "t", "input_schema": {"type": "object"}},
        _passthrough,
    )
    outside = registry.definitions()
    outside.clear()
    assert [d["name"] for d in registry.definitions()] == ["t"]


# ---------------------------------------------------------------------------
# Permission filtering — definitions(allowed=...) and execute(allowed=...)
# ---------------------------------------------------------------------------


def _three_tool_registry() -> ToolRegistry:
    """Build a registry with three tools, useful for filter-behavior tests."""
    registry = ToolRegistry()
    for name in ("read_chart", "write_task", "send_message"):
        registry.register(
            {"name": name, "description": name, "input_schema": {"type": "object"}},
            _passthrough,
        )
    return registry


def test_definitions_with_no_allowed_returns_everything() -> None:
    """Default behavior is backwards-compatible — no filter, all tools served."""
    registry = _three_tool_registry()
    assert sorted(d["name"] for d in registry.definitions()) == [
        "read_chart",
        "send_message",
        "write_task",
    ]


def test_definitions_with_allowed_filters_to_named_tools() -> None:
    """Passing allowed=... narrows the catalog before the model sees it."""
    registry = _three_tool_registry()
    filtered = registry.definitions(allowed={"read_chart", "write_task"})
    assert sorted(d["name"] for d in filtered) == ["read_chart", "write_task"]


def test_definitions_with_empty_allowed_returns_nothing() -> None:
    """allowed=set() is the "no tools" surface — distinct from allowed=None."""
    registry = _three_tool_registry()
    assert registry.definitions(allowed=set()) == []


def test_definitions_silently_ignores_unknown_names_in_allowed() -> None:
    """A manifest typo in the allowlist must NOT surface phantom tools to the model."""
    registry = _three_tool_registry()
    filtered = registry.definitions(allowed={"read_chart", "definitely-not-a-tool"})
    assert [d["name"] for d in filtered] == ["read_chart"]


def test_execute_with_no_allowed_dispatches_as_before() -> None:
    """Default execute() behavior is unchanged — no filter."""
    registry = _three_tool_registry()
    result = registry.execute("read_chart", {"x": 1}, ctx={})
    assert result["args"] == {"x": 1}


def test_execute_with_allowed_dispatches_when_name_in_set() -> None:
    """A tool name in the allowlist executes normally."""
    registry = _three_tool_registry()
    result = registry.execute("read_chart", {"x": 1}, ctx={}, allowed={"read_chart", "write_task"})
    assert result["args"] == {"x": 1}


def test_execute_with_allowed_raises_when_name_not_in_set() -> None:
    """A registered tool that's outside the allowlist raises ToolNotAllowed."""
    registry = _three_tool_registry()
    with pytest.raises(ToolNotAllowed, match="not in the caller's allowed set"):
        registry.execute("send_message", {}, ctx={}, allowed={"read_chart", "write_task"})


def test_execute_distinguishes_unknown_from_not_allowed() -> None:
    """ValueError ("Unknown tool") and ToolNotAllowed are distinct, not aliased."""
    registry = _three_tool_registry()
    # Truly unregistered → ValueError, not ToolNotAllowed.
    with pytest.raises(ValueError, match="Unknown tool"):
        registry.execute("ghost", {}, ctx={}, allowed={"ghost"})


def test_tool_not_allowed_is_a_lookup_error() -> None:
    """ToolNotAllowed inherits from LookupError so callers can broaden if useful."""
    assert issubclass(ToolNotAllowed, LookupError)
