from abc import ABC, abstractmethod
from typing import Any

from canvas_sdk.agents.gateway import LLMGateway
from canvas_sdk.agents.result import AgentRunResult
from canvas_sdk.agents.state import AgentState
from canvas_sdk.agents.tool_loop import ToolLoopResult, run_tool_loop
from canvas_sdk.agents.tool_registry import ToolRegistry


class AgentPlugin(ABC):
    """Base class for agents invoked by the ``run_agent`` Celery task.

    Not a :class:`canvas_sdk.handlers.BaseHandler`: agents do not register
    for events and have no ``compute()``. A trigger handler (which IS a
    :class:`BaseHandler`) emits a ``RunAgentEffect``; the platform
    interpreter enqueues the ``run_agent`` task; the worker instantiates
    this class by class path and invokes the three required methods in
    order — ``load_state`` → ``run`` → ``save_state``. Runs of one agent
    on one ``scope_key`` happen one at a time, each starting after the
    previous run's effects have been applied.
    """

    # The agent's tool registry. Set as a class attribute by subclasses
    # to the module-level registry the agent uses (e.g., ``tools =
    # chart_chat_tools_registry``). Before ``run()`` fires, the
    # platform replaces this with a *scoped* view containing only the
    # tools the manifest's ``components.agents[].tools`` grants; an agent
    # whose manifest grants nothing gets an empty registry. The agent uses
    # ``self.tools.definitions()`` / ``self.tools.execute(...)`` directly
    # and the ungranted entries aren't reachable.
    #
    # The grant also bounds the agent's output: the platform drops any
    # effect in ``AgentRunResult.effects`` whose type no granted tool
    # declares (``ToolRegistry.effect_types``), so building an effect
    # directly, or through the module-level registry, can't widen it.
    tools: ToolRegistry | None = None

    # The tool names the manifest grants this run, set by the platform on
    # the agent instance before lifecycle hooks fire. Empty when the
    # manifest grants none.
    tools_allowed: frozenset[str] = frozenset()

    @abstractmethod
    def load_state(self, scope_key: str) -> AgentState:
        """Load this run's starting state from per-EHR storage."""
        ...

    @abstractmethod
    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict[str, Any],
    ) -> AgentRunResult:
        """Drive the agent. Return updated state and effects to emit."""
        ...

    @abstractmethod
    def save_state(self, scope_key: str, state: AgentState) -> None:
        """Write the updated state back to per-EHR storage."""
        ...

    def on_run_start(self, scope_key: str) -> None:
        """Optional hook fired before ``load_state``. Default: no-op."""
        return None

    def on_turn(self, turn_index: int) -> None:
        """Optional hook fired before each LLM call ``run_tool_loop`` makes. Default: no-op."""
        return None

    def run_tool_loop(
        self,
        gateway: LLMGateway,
        *,
        ctx: dict[str, Any],
        system: str,
        messages: list[dict[str, Any]],
        **options: Any,
    ) -> ToolLoopResult:
        """Run :func:`canvas_sdk.agents.run_tool_loop` with this agent's tools and hooks.

        Uses ``self.tools``, the registry scoped to the manifest's grant, and calls
        :meth:`on_turn` before each LLM call. ``options`` are the remaining
        ``run_tool_loop`` arguments (``max_turns``, ``max_tokens``, ``model``,
        ``history_chars``, ``cache_system``).
        """
        return run_tool_loop(
            gateway,
            tools=self.tools or ToolRegistry(),
            ctx=ctx,
            system=system,
            messages=messages,
            on_turn=self.on_turn,
            **options,
        )

    def on_run_end(self, result: AgentRunResult) -> None:
        """Optional hook fired after ``run`` returns successfully. Default: no-op."""
        return None

    def on_run_error(self, exc: BaseException) -> None:
        """Optional hook fired if ``run`` raises. Default: no-op."""
        return None


__exports__ = ("AgentPlugin",)
