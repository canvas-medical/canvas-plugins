"""What became of a chat agent's proposals, recorded in its conversation for the model.

A change an approval-listed tool stages waits for the person the agent acted for. When they
approve, deny, or let it expire, the next run adds one note to the conversation saying so,
so the model never treats a decided change as pending or a denied one as made. The note
is the chat's, not the person's, and the chat UIs leave it out of what they show.
"""

import json
from typing import Any

from canvas_sdk.v1.data import AgentRunProposal, AgentRunProposalStatus

# Every chat's note starts with this, so a UI can tell it from a person's message.
NOTE_START = "[Approval decisions, recorded by the chat"


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
        and str(content[0].get("text", "")).startswith(NOTE_START)
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
