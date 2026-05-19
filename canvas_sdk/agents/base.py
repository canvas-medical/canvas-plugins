from abc import ABC, abstractmethod
from typing import Any

from canvas_sdk.agents.gateway import LLMGateway
from canvas_sdk.agents.result import AgentRunResult
from canvas_sdk.agents.state import AgentState


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
