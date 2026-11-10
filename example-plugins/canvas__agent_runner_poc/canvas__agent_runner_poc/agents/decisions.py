"""What became of a chat agent's proposals, recorded in its conversation for the model.

A change an approval-listed tool stages waits for the person the agent acted for. When they
approve, deny, or let it expire, the next run adds one note to the conversation saying so,
so the model never treats a decided change as pending or a denied one as made.

A run's state is saved when the plugin returns, before Canvas applies its changes, and
Canvas can refuse them, apply none after the run lost its scope, or stop at one that
fails. So the next run also checks the platform's record of the run before it, and when
fewer changes reached Canvas than the run returned, adds a note saying so.

The notes are the chat's, not the person's, and the chat UIs leave them out of what they
show.
"""

import json
from typing import Any

from canvas_sdk.agents import AgentPlugin
from canvas_sdk.v1.data import AgentRun, AgentRunProposal, AgentRunProposalStatus

# Every chat's note starts with one of these, so a UI can tell it from a person's message.
NOTE_START = "[Approval decisions, recorded by the chat"
UNAPPLIED_START = "[Changes not applied, recorded by the chat"


def note_prefix(who: str) -> str:
    """The opening line of the note, naming who decides, such as "clinician"."""
    return f"{NOTE_START}, not from the {who}]"


def _decision_text(status: str, who: str) -> str:
    return {
        AgentRunProposalStatus.APPROVED: f"approved by the {who} and applied",
        AgentRunProposalStatus.DENIED: f"denied by the {who}; nothing changed",
        AgentRunProposalStatus.FAILED: "approved, but could not be applied; nothing changed",
        AgentRunProposalStatus.EXPIRED: "expired without a decision; nothing changed",
    }[status]


def is_decisions_note(message: dict[str, Any]) -> bool:
    """Whether ``message`` is the chat's note of proposal decisions rather than a person's."""
    content = message.get("content")
    return (
        message.get("role") == "user"
        and isinstance(content, list)
        and len(content) == 1
        and isinstance(content[0], dict)
        and str(content[0].get("text", "")).startswith((NOTE_START, UNAPPLIED_START))
    )


def _proposed_ids(messages: list[dict[str, Any]]) -> list[str]:
    """The proposal ids the tool results in ``messages`` told the model are awaiting approval."""
    ids: list[str] = []
    for message in messages:
        content = message.get("content")
        if message.get("role") != "user" or not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            try:
                result = json.loads(block.get("content") or "")
            except ValueError:
                continue
            if isinstance(result, dict) and result.get("status") == "awaiting_approval":
                ids.extend(str(proposal_id) for proposal_id in result.get("proposal_ids") or [])
    return ids


def record_decisions(
    messages: list[dict[str, Any]], staff_id: str, who: str
) -> list[dict[str, Any]]:
    """Return ``messages`` with a note of the proposals decided since the model last heard.

    A proposal the conversation is still waiting on, and that ``who`` (the staff member
    ``staff_id``) has approved, denied, or let expire, goes into one note.
    """
    recorded = "\n".join(
        str(message["content"][0]["text"]) for message in messages if is_decisions_note(message)
    )
    waiting = [
        proposal_id for proposal_id in _proposed_ids(messages) if proposal_id not in recorded
    ]
    if not waiting:
        return messages
    decided = (
        AgentRunProposal.objects.filter(id__in=waiting, staff__id=staff_id)
        .exclude(status=AgentRunProposalStatus.PENDING)
        .order_by("created_at")
    )
    lines = []
    for proposal in decided:
        line = f"- proposal {proposal.id} ({proposal.tool}): {_decision_text(proposal.status, who)}"
        if proposal.reason:
            line += f". Reason: {proposal.reason}"
        lines.append(line)
    if not lines:
        return messages
    note = "\n".join([note_prefix(who), *lines])
    return [*messages, {"role": "user", "content": [{"type": "text", "text": note}]}]


def record_unapplied(
    messages: list[dict[str, Any]], agent: AgentPlugin, scope_key: str, who: str
) -> list[dict[str, Any]]:
    """Return ``messages`` with a note when the previous run's changes did not all apply.

    The previous run is the latest finished run of ``agent`` on ``scope_key``, the
    conversation's, before this one, which ``who`` started. Canvas records how many effects it
    returned, how many the grant dropped, and how many were applied; fewer applied than
    kept means the saved conversation claims changes that were not made.
    """
    agent_id = f"{type(agent).__module__}:{type(agent).__name__}"
    previous = (
        AgentRun.objects.filter(
            agent_id=agent_id,
            scope_key=scope_key,
            finished_at__isnull=False,
            effects_returned__isnull=False,
        )
        .exclude(id=agent.run_id)
        .order_by("-queued_at")
        .first()
    )
    if previous is None:
        return messages
    kept = previous.effects_returned - (previous.effects_dropped or 0)
    applied = previous.effects_applied or 0
    recorded = "\n".join(
        str(message["content"][0]["text"]) for message in messages if is_decisions_note(message)
    )
    if applied >= kept or str(previous.id) in recorded:
        return messages
    note = (
        f"{UNAPPLIED_START}, not from the {who}]\n"
        f"- run {previous.id}: {kept - applied} of the {kept} changes your last reply "
        f"staged did not reach the chart ({previous.status}"
        + (f": {previous.error}" if previous.error else "")
        + "). Do not say they were made; check the chart before relying on them."
    )
    return [*messages, {"role": "user", "content": [{"type": "text", "text": note}]}]
