"""Proposals: how an approval-listed tool's changes wait for the requester.

The platform wraps each effect such a tool stages in a ``PROPOSE_AGENT_ACTION`` effect,
which home-app holds until the requester approves or denies it. Not importable from the
plugin sandbox: plugin code decides with :class:`canvas_sdk.effects.agent.DecideAgentProposal`.
"""

import json
from typing import Any
from uuid import uuid4

from canvas_sdk.effects import Effect, EffectType

PROPOSAL_EFFECT_TYPE = "PROPOSE_AGENT_ACTION"
DECISION_EFFECT_TYPE = "DECIDE_AGENT_PROPOSAL"


def propose(effect: Effect, tool: str, arguments: dict[str, Any]) -> Effect:
    """Wrap ``effect``, which ``tool`` staged from ``arguments``, as a proposal."""
    return Effect(
        type=EffectType.PROPOSE_AGENT_ACTION,
        payload=json.dumps(
            {
                "data": {
                    "proposal_id": str(uuid4()),
                    "tool": tool,
                    "arguments": arguments,
                    "effect": {"type": EffectType.Name(effect.type), "payload": effect.payload},
                }
            },
            default=str,
        ),
    )


def proposal_id(proposal: Effect) -> str:
    """The id a proposal effect carries."""
    return str(json.loads(proposal.payload)["data"]["proposal_id"])


def proposed_effect_type(proposal: Effect) -> str:
    """The ``EffectType`` name of the change a proposal effect wraps."""
    return str(json.loads(proposal.payload)["data"]["effect"]["type"])


# Nothing here is importable from the plugin sandbox.
__exports__ = ()
