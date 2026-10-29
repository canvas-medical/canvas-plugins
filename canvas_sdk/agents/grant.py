"""How the platform applies an agent's manifest tool grant.

The plugin-runner and :mod:`canvas_sdk.test_utils.agents` both call these, so a test
sees exactly the tools and effects a real run would. Not importable from the plugin
sandbox.
"""

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.agents.tool_registry import ToolRegistry

if TYPE_CHECKING:
    from canvas_sdk.agents.base import AgentPlugin
    from canvas_sdk.effects import Effect


def apply_tool_grant(agent: "AgentPlugin", grant: Mapping[str, Any]) -> frozenset[str]:
    """Scope ``agent.tools`` to the manifest's ``tools`` grant; return the effect types it allows.

    ``allowed`` holds tool names and ``@category`` references, ``denied`` is subtracted
    after expansion, and a grant with nothing allowed gives the agent no tools. Sets
    ``agent.tools_allowed`` and replaces ``agent.tools`` with the scoped view.
    """
    registry = agent.tools or ToolRegistry()
    agent.tools_allowed = registry.resolve_allowed(
        grant.get("allowed") or (),
        denied=grant.get("denied"),
    )
    agent.tools = registry.scope(agent.tools_allowed)
    return agent.tools.effect_types()


def split_granted_effects(
    effects: Iterable["Effect"], granted_effect_types: frozenset[str]
) -> tuple[list["Effect"], list["Effect"]]:
    """Split returned effects into those a granted tool stages and those the grant drops."""
    kept: list[Effect] = []
    dropped: list[Effect] = []
    for effect in effects:
        (kept if EffectType.Name(effect.type) in granted_effect_types else dropped).append(effect)
    return kept, dropped


# Nothing here is importable from the plugin sandbox.
__exports__ = ()
