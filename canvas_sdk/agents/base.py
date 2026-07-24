from abc import ABC, abstractmethod
from typing import Any

from canvas_sdk.agents.gateway import LLMGateway
from canvas_sdk.agents.result import AgentRunResult
from canvas_sdk.agents.state import AgentState
from canvas_sdk.agents.tool_registry import ToolRegistry


class AgentPlugin(ABC):
    """Base class for agents invoked by the ``run_agent`` Celery task.

    Not a :class:`canvas_sdk.handlers.BaseHandler`: agents do not register
    for events and have no ``compute()``. A trigger handler (which IS a
    :class:`BaseHandler`) emits a ``RunAgentEffect``; the platform
    interpreter enqueues the ``run_agent`` task; the worker instantiates
    this class by class path and invokes the three required methods in
    order — ``load_state`` → ``run`` → ``save_state`` — with the
    per-``scope_key`` lock held the entire time.
    """

    # The agent's tool registry. Set as a class attribute by subclasses
    # to the module-level registry the agent uses (e.g., ``tools =
    # chart_chat_tools_registry``). Before ``run()`` fires, the
    # platform replaces this with a *scoped* view containing only the
    # tools allowed by the manifest's
    # ``components.agents[].tools.allowed``; the agent uses
    # ``self.tools.definitions()`` / ``self.tools.execute(...)``
    # directly and the disallowed entries simply aren't reachable. PoC:
    # the agent must use ``self.tools`` rather than importing the
    # underlying module-level registry to get the filtered view. True
    # sandbox-level isolation (preventing access to the unfiltered
    # registry) is V1+.
    #
    # ``None`` is the default — agents that don't declare a class-level
    # ``tools`` attribute (e.g., agents with no tool use) get no
    # enforcement seam and no scoping happens.
    tools: ToolRegistry | None = None

    # Per-run tool allowlist (the source of ``tools`` scoping above).
    # Sourced from ``components.agents[].tools.allowed`` at load time
    # and set by the platform on the agent instance before lifecycle
    # hooks fire. ``None`` (no manifest declaration) means no scoping
    # — the agent sees every tool registered on its registry.
    tools_allowed: frozenset[str] | None = None

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
        """Optional hook fired at the start of each LLM turn. Default: no-op."""
        return None

    def on_run_end(self, result: AgentRunResult) -> None:
        """Optional hook fired after ``run`` returns successfully. Default: no-op."""
        return None

    def on_run_error(self, exc: BaseException) -> None:
        """Optional hook fired if ``run`` raises. Default: no-op."""
        return None


__exports__ = ("AgentPlugin",)
