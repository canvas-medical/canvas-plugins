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
    proposed_effect_types,
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
        proposal of one. A proposal must carry at least one change, and every change it
        carries must be one an approval-listed tool stages.
        """
        name = EffectType.Name(effect.type)
        if name == DECISION_EFFECT_TYPE:
            return False
        if name == PROPOSAL_EFFECT_TYPE:
            try:
                proposed = proposed_effect_types(effect)
            except (ValueError, KeyError, TypeError):
                # A payload the platform cannot read is dropped like any effect it
                # cannot allow, rather than failing a run whose state is already saved.
                return False
            return bool(proposed) and all(
                each in self.proposable and each not in (PROPOSAL_EFFECT_TYPE, DECISION_EFFECT_TYPE)
                for each in proposed
            )
        return name in self.direct


# Changes the platform accepts only through the requester's approval: a commit is the user
# attesting to the command, a lab report puts results in the chart with no draft, and these
# originates commit what they draft.
_APPROVAL_ONLY_EFFECT_TYPES = frozenset(
    name
    for name in EffectType.DESCRIPTOR.values_by_name
    if name.startswith("COMMIT_") and name.endswith("_COMMAND")
) | {
    "CREATE_LAB_REPORT",
    "ATTACH_LAB_REPORT_RESULTS",
    "ORIGINATE_CUSTOM_COMMAND_COMMAND",
    "ORIGINATE_CHART_SECTION_REVIEW_COMMAND",
}


def _approval_closure(tools: ToolRegistry, approve: frozenset[str]) -> frozenset[str]:
    """``approve``, every tool staging an approval-only change, and every tool that stages
    an effect type one of those stages.

    The grant check sees effect types, not which tool staged an effect, so a change one
    tool may only propose cannot also be one another granted tool makes directly. A
    change the platform accepts only through approval is proposed whatever the manifest
    lists, so it never reaches the platform bare.
    """
    names = [definition["name"] for definition in tools.definitions()]
    closed = set(approve) | {
        name for name in names if tools.effect_types_for(name) & _APPROVAL_ONLY_EFFECT_TYPES
    }
    while True:
        proposable = frozenset().union(*(tools.effect_types_for(name) for name in closed))
        widened = {name for name in names if tools.effect_types_for(name) & proposable}
        if widened <= closed:
            return frozenset(closed)
        closed |= widened


def grant_problems(tools: ToolRegistry, grant: Mapping[str, Any]) -> list[str]:
    """What is wrong with a manifest ``tools`` grant for an agent whose registry is ``tools``.

    Each key must be a list of tool names and ``@category`` groups. An ``approve`` or
    ``denied`` entry that names no tool on the registry is a problem, since a misspelling
    would silently lift an approval or a denial; an ``allowed`` entry only adds tools, so
    a name the registry lacks grants nothing and is no problem.
    """
    problems = []
    for key in ("allowed", "approve", "denied"):
        entries = grant.get(key)
        if entries is None:
            continue
        if not isinstance(entries, list) or not all(isinstance(e, str) for e in entries):
            problems.append(f"tools.{key} must be a list of tool names and @category groups")
            continue
        if key != "allowed":
            problems.extend(
                f"tools.{key} names no tool: {entry!r}"
                for entry in entries
                if not tools.resolve_allowed([entry])
            )
    return problems


def apply_tool_grant(agent: "AgentPlugin", grant: Mapping[str, Any]) -> EffectGrant:
    """Scope ``agent.tools`` to what the run may use; return what the agent may return.

    That is the manifest's ``tools`` grant less the tools the run's requester could not
    use: those needing a permission ``agent.requester`` lacks or a capability
    ``agent.capabilities`` lacks, so set both first. ``allowed`` holds tool names and
    ``@category`` references, ``denied`` is subtracted after expansion, and a grant
    with nothing allowed gives the agent no tools. Tools ``approve`` names, in the same
    shape, propose their changes for the requester to approve, and so does any granted
    tool that stages an effect type one of them stages. Sets
    ``agent.tools_allowed`` and replaces ``agent.tools`` with the scoped view. A grant
    :func:`grant_problems` faults raises ``ValueError``, so the run fails rather than
    running with a gate lifted.
    """
    registry = agent.tools or ToolRegistry()
    if problems := grant_problems(registry, grant):
        raise ValueError(f"The agent's tools grant is invalid: {'; '.join(problems)}")
    granted = registry.scope(
        registry.resolve_allowed(grant.get("allowed") or (), denied=grant.get("denied"))
    )
    usable = granted.usable_by(agent.requester.permissions, agent.capabilities)
    agent.tools = usable.with_approval(
        _approval_closure(usable, usable.resolve_allowed(grant.get("approve") or ()))
    )
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
