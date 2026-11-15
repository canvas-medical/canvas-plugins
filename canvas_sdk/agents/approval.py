"""Proposals: how an approval-listed tool's changes wait for the requester.

The platform wraps the effects one call of such a tool stages, in order, in one
``PROPOSE_AGENT_ACTION`` effect, which home-app holds until the requester approves or
denies the whole call. A tool that stages a note and a plan on it is one decision, so the
plan can neither apply nor be approved without its note. Not importable from the plugin
sandbox: plugin code decides with :class:`canvas_sdk.effects.agent.DecideAgentProposal`.
"""

import json
from typing import Any
from uuid import uuid4

from canvas_sdk.effects import Effect, EffectType

PROPOSAL_EFFECT_TYPE = "PROPOSE_AGENT_ACTION"
DECISION_EFFECT_TYPE = "DECIDE_AGENT_PROPOSAL"


def propose(effects: list[Effect], tool: str, arguments: dict[str, Any]) -> Effect:
    """Wrap ``effects``, which one call of ``tool`` staged from ``arguments``, as a proposal."""
    return Effect(
        type=EffectType.PROPOSE_AGENT_ACTION,
        payload=json.dumps(
            {
                "data": {
                    "proposal_id": str(uuid4()),
                    "tool": tool,
                    "arguments": arguments,
                    "effects": [
                        {"type": EffectType.Name(effect.type), "payload": effect.payload}
                        for effect in effects
                    ],
                }
            },
            default=str,
        ),
    )


def proposal_id(proposal: Effect) -> str:
    """The id a proposal effect carries."""
    return str(json.loads(proposal.payload)["data"]["proposal_id"])


def proposed_effect_types(proposal: Effect) -> list[str]:
    """The ``EffectType`` names of the changes a proposal effect wraps, in order."""
    return [str(effect["type"]) for effect in json.loads(proposal.payload)["data"]["effects"]]


# Nothing here is importable from the plugin sandbox.
__exports__ = ()
