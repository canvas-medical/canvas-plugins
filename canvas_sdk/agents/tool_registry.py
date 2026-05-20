from collections.abc import Callable, Iterable
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


class ToolNotAllowed(LookupError):
    """Raised by :meth:`ToolRegistry.execute` when a registered tool is filtered out.

    Distinct from ``ValueError("Unknown tool: ...")`` (raised when the tool
    isn't registered at all). A ``ToolNotAllowed`` means the tool exists in
    the registry but is excluded by the caller's allowlist — typically
    because the agent's manifest doesn't grant it, or because the agent
    deliberately narrows its tool surface for a particular run.
    """


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

    def definitions(self, *, allowed: Iterable[str] | None = None) -> list[dict[str, Any]]:
        """Tool list suitable for ``client.messages.create(tools=...)``.

        Args:
            allowed: Optional iterable of tool names to include. When supplied,
                only tools whose ``name`` appears in the iterable are returned;
                others are filtered out before the model ever sees them. Names
                in ``allowed`` that aren't registered are silently ignored
                (defense in depth — a manifest typo doesn't surface anything
                extra to the model). When ``None`` (the default), every
                registered tool is returned.
        """
        if allowed is None:
            return list(self._definitions)
        allowed_set = set(allowed)
        return [d for d in self._definitions if d["name"] in allowed_set]

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        ctx: dict[str, Any],
        allowed: Iterable[str] | None = None,
    ) -> Any:
        """Dispatch a model-issued tool call to the registered executor.

        Args:
            name: The tool's registered name (the ``"name"`` key from its
                JSON-Schema definition).
            arguments: The model's ``tool_use.input`` dict — values the model
                chose. Passed through to the executor as-is.
            ctx: Platform-supplied per-run context (``patient_id``, ``note_id``,
                the effects accumulator, etc.) the model never sees.
            allowed: If supplied, ``name`` must be in this iterable in addition
                to being registered — otherwise raises :class:`ToolNotAllowed`.
                Pass the same allowlist you passed to :meth:`definitions` so
                the model can't sneak past the catalog filter (e.g., by
                replaying a tool name it remembers from a previous turn that
                used a different allowlist).

        Raises:
            ValueError: If ``name`` is not a registered tool. The caller is
                expected to translate this into a ``tool_result`` with
                ``is_error=True`` rather than crashing the run.
            ToolNotAllowed: If ``allowed`` was supplied and ``name`` is not in it.
        """
        executor = self._executors.get(name)
        if executor is None:
            raise ValueError(f"Unknown tool: {name!r}")
        if allowed is not None and name not in set(allowed):
            raise ToolNotAllowed(f"Tool {name!r} is registered but not in the caller's allowed set")
        return executor(arguments, ctx=ctx)


__exports__ = ("ToolNotAllowed", "ToolRegistry")
