from typing import Any

import pytest

from canvas_sdk.agents import ToolRegistry


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
