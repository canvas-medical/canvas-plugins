from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from canvas_sdk.agents.state import AgentState

if TYPE_CHECKING:
    from canvas_sdk.effects import Effect


@dataclass
class AgentRunResult:
    """Return value from AgentPlugin.run().

    Carries the (possibly mutated) state — to be persisted by save_state —
    and the effects to be dispatched through handle_effect after run()
    returns and save_state commits.
    """

    state: AgentState
    effects: list["Effect"] = field(default_factory=list)


__exports__ = ("AgentRunResult",)
