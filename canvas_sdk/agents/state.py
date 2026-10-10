from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    """Per-(agent, scope_key) state container passed in and out of AgentPlugin.run().

    The PoC default is a generic dict store. Plugin authors who want typed
    state subclass this and add their own fields; the framework only cares
    that load_state returns an AgentState and that run() returns one back
    inside an AgentRunResult.
    """

    data: dict[str, Any] = field(default_factory=dict)


__exports__ = ("AgentState",)
