"""How the platform applies an agent's manifest tool grant.

The plugin-runner and :mod:`canvas_sdk.test_utils.agents` both call these, so a test
sees exactly the tools and effects a real run would. Not importable from the plugin
sandbox.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.agents.approval import (
    DECISION_EFFECT_TYPE,
    PROPOSAL_EFFECT_TYPE,
    proposed_effect_type,
)
from canvas_sdk.agents.tool_registry import ToolRegistry

if TYPE_CHECKING:
    from canvas_sdk.agents.base import AgentPlugin
    from canvas_sdk.effects import Effect


@dataclass(frozen=True)
class EffectGrant:
    """What a run's granted tools let its agent return.

    ``direct`` are the effect types a tool that needs no approval stages. ``proposable``
    are the types a tool that needs approval stages, which the agent may return only
    wrapped in a proposal, so a change listed for approval cannot be returned bare.
    """

    direct: frozenset[str]
    proposable: frozenset[str]

    def allows(self, effect: "Effect") -> bool:
        """Whether the agent may return ``effect``.

        Never a decision on a proposal, which only the requester makes, and never a
        proposal of one.
        """
        name = EffectType.Name(effect.type)
        if name == DECISION_EFFECT_TYPE:
            return False
        if name == PROPOSAL_EFFECT_TYPE:
            proposed = proposed_effect_type(effect)
            return proposed in self.proposable and proposed not in (
                PROPOSAL_EFFECT_TYPE,
                DECISION_EFFECT_TYPE,
            )
        return name in self.direct


def apply_tool_grant(agent: "AgentPlugin", grant: Mapping[str, Any]) -> EffectGrant:
    """Scope ``agent.tools`` to what the run may use; return what the agent may return.

    That is the manifest's ``tools`` grant less the tools the run's requester could not
    use: those needing a permission ``agent.requester`` lacks or a capability
    ``agent.capabilities`` lacks, so set both first. ``allowed`` holds tool names and
    ``@category`` references, ``denied`` is subtracted after expansion, and a grant
    with nothing allowed gives the agent no tools. Tools ``approve`` names, in the same
    shape, propose their changes for the requester to approve. Sets
    ``agent.tools_allowed`` and replaces ``agent.tools`` with the scoped view.
    """
    registry = agent.tools or ToolRegistry()
    granted = registry.scope(
        registry.resolve_allowed(grant.get("allowed") or (), denied=grant.get("denied"))
    )
    usable = granted.usable_by(agent.requester.permissions, agent.capabilities)
    agent.tools = usable.with_approval(usable.resolve_allowed(grant.get("approve") or ()))
    agent.tools_allowed = frozenset(d["name"] for d in agent.tools.definitions())
    return EffectGrant(
        direct=agent.tools.direct_effect_types(),
        proposable=agent.tools.proposable_effect_types(),
    )


def split_granted_effects(
    effects: Iterable["Effect"], grant: EffectGrant
) -> tuple[list["Effect"], list["Effect"]]:
    """Split returned effects into those the grant allows and those it drops."""
    kept: list[Effect] = []
    dropped: list[Effect] = []
    for effect in effects:
        (kept if grant.allows(effect) else dropped).append(effect)
    return kept, dropped


# Nothing here is importable from the plugin sandbox.
__exports__ = ()
