from collections.abc import Callable
from typing import Any, Protocol


class ToolExecutor(Protocol):
    """Executor signature: ``fn(arguments, *, ctx)`` returning a JSON-serializable value.

    ``arguments`` is the model's ``tool_use.input`` dict — values the model chose.
    ``ctx`` is the platform's per-run context (``patient_id``, ``note_id``,
    ``effects`` accumulator, etc.) — values the model never sees and never chooses.
    """

    def __call__(self, arguments: dict[str, Any], *, ctx: dict[str, Any]) -> Any:
        """Run the tool with model-supplied ``arguments`` and platform-supplied ``ctx``."""
        ...


class ToolRegistry:
    """A composable catalog of agent tools.

    Pairs each tool's JSON-Schema definition with its executor so they can't
    drift apart. Supports two registration styles:

    1. **Decorator** for inline definition::

        @registry.tool(
            name="find_medications",
            description="...",
            input_schema={...},
        )
        def _find_medications(arguments, *, ctx):
            ...

    2. **Imperative** ``register(definition, executor)`` for cases where the
       definition is built elsewhere (e.g., auto-generated from an effect proto).

    The platform-provided :data:`canvas_sdk.agents.standard_tools` is the
    canonical SDK-side registry; plugin authors call
    ``my_registry.extend(standard_tools)`` to adopt the SDK catalog and then
    layer their own tools on top.
    """

    def __init__(self) -> None:
        self._definitions: list[dict[str, Any]] = []
        self._executors: dict[str, ToolExecutor] = {}

    def register(self, definition: dict[str, Any], executor: ToolExecutor) -> None:
        """Register a tool by passing the definition and executor directly.

        Raises:
            ValueError: If ``definition`` is missing a ``"name"`` key or if a
                tool with that name is already registered.
        """
        name = definition.get("name")
        if not name:
            raise ValueError("Tool definition is missing a 'name' key")
        if name in self._executors:
            raise ValueError(f"Tool {name!r} is already registered")
        self._definitions.append(definition)
        self._executors[name] = executor

    def tool(
        self,
        *,
        name: str,
        description: str,
        input_schema: dict[str, Any],
    ) -> Callable[[ToolExecutor], ToolExecutor]:
        """Decorator form for registering a tool inline with its executor."""

        def decorator(fn: ToolExecutor) -> ToolExecutor:
            self.register(
                {"name": name, "description": description, "input_schema": input_schema},
                fn,
            )
            return fn

        return decorator

    def extend(self, other: "ToolRegistry") -> None:
        """Copy every tool from ``other`` into this registry.

        Mutations to ``self`` after the call don't affect ``other`` and vice
        versa — this is a shallow copy of definitions and an executor-ref copy
        of executors. Plugin code typically calls this once at module import
        time to adopt the SDK's :data:`standard_tools` catalog.

        Raises:
            ValueError: On name collisions between the two registries.
        """
        for definition in other._definitions:
            self.register(dict(definition), other._executors[definition["name"]])

    def definitions(self) -> list[dict[str, Any]]:
        """Tool list suitable for ``client.messages.create(tools=...)``."""
        return list(self._definitions)

    def execute(self, name: str, arguments: dict[str, Any], *, ctx: dict[str, Any]) -> Any:
        """Dispatch a model-issued tool call to the registered executor.

        Raises:
            ValueError: If ``name`` is not a registered tool. The caller is
                expected to translate this into a ``tool_result`` with
                ``is_error=True`` rather than crashing the run.
        """
        executor = self._executors.get(name)
        if executor is None:
            raise ValueError(f"Unknown tool: {name!r}")
        return executor(arguments, ctx=ctx)


__exports__ = ("ToolRegistry",)
