"""ClaimsChatAgent — a chat agent for billing staff working claims.

The chat opens in one of two modes, chosen by the effect that starts the run:

- **Queue mode** (``Scope.STAFF``, no claim): the staff member's conversation about
  their claims work across the queues, one per staff member.
- **Claim mode** (``Scope.CLAIM`` with ``claim_id``): a conversation about one claim,
  one per staff member and claim. The platform checks the claim exists and that the
  requester has the revenue capability, and the claims tools default to the claim.

The tools are the SDK's claims tools, granted in the manifest as ``@claims_reads``
and ``@claims_writes``. They refuse without :attr:`Capability.REVENUE`, which the
platform grants only to staff with revenue access to every patient. A queue-mode run
from a staff member without it answers that directly, without calling the model.

State follows the chart chat's snapshot pattern over :class:`ClaimConversation`.
"""

from typing import Any

from agent_runner_poc.models.claim_conversation import ClaimConversation
from agent_runner_poc.models.proxy import StaffProxy
from canvas_sdk.agents import (
    DEFAULT_HISTORY_CHARS,
    AgentPlugin,
    AgentRunResult,
    AgentState,
    Capability,
    LLMGateway,
    ToolRegistry,
    standard_tools,
    window_messages,
)
from logger import log

SYSTEM_PROMPT = (
    "You are a revenue-cycle assistant for billing staff working insurance claims in "
    "Canvas. You answer questions about claims and, when the user asks, make workflow "
    "changes to them.\n\n"
    "Tools:\n"
    "- Reads: `find_claims` (filter by queue, patient, assignee, label, payer, balance, "
    "date of service), `summarize_claims` (counts and balances per queue), `get_claim` "
    "(one claim's coverages, providers, diagnosis codes, line items, banners, comments), "
    "`find_claim_queues`, `find_claim_labels`, `find_claim_assignees`.\n"
    "- Writes: `move_claim_to_queue`, `assign_claim`, `unassign_claim`, "
    "`add_claim_labels`, `remove_claim_labels`, `add_claim_comment`, "
    "`add_claim_banner`, `remove_claim_banner`. Each change applies when your reply "
    "finishes.\n\n"
    "Rules:\n"
    "- Answer questions with reads only. Make a change only when the user asks for it.\n"
    "- Before changing more than one claim, list the claims you would change and ask "
    "the user to confirm.\n"
    "- After a change, say exactly what you changed on which claim.\n"
    "- Do not choose or suggest procedure codes, diagnosis codes, or modifiers; that is "
    "for coders and clinicians. You may point out what looks inconsistent on a claim, "
    "such as a line item with no linked diagnosis or an inactive coverage.\n"
    "- You cannot submit claims, post payments, edit line items, or trash a claim; say "
    "so when asked.\n"
    "- Write every claim id in full so the user can open that claim's chat from it.\n"
    "- Plain text only, no markdown headings. Keep answers short."
)

QUEUE_MODE = (
    "\n\nThis conversation is about the user's work across the claims queues. Find the "
    "claims you need with `find_claims` or `summarize_claims`."
)

CLAIM_MODE = (
    "\n\nThis conversation is about claim {claim_id}. Tools that take a `claim_id` act on "
    "it when you leave `claim_id` out. Read it with `get_claim` before answering."
)

NO_REVENUE_ACCESS = (
    "I can't work claims for you: that needs the Revenue access permission and access "
    "to every patient. Ask an administrator if you need it."
)

MAX_TURNS = 10

STORED_HISTORY_CHARS = 2 * DEFAULT_HISTORY_CHARS

tools = ToolRegistry()
tools.extend(standard_tools)


def load_claims_conversation(staff_id: str, claim_id: str | None) -> list[dict[str, Any]]:
    """A staff member's message history about one claim, or about the queues with no claim."""
    conversation = ClaimConversation.objects.filter(
        staff__id=staff_id, claim_id=claim_id or ""
    ).first()
    return list(conversation.messages or []) if conversation else []


def _save_claims_conversation(
    staff_id: str,
    claim_id: str | None,
    messages: list[dict[str, Any]],
) -> None:
    conversation = ClaimConversation.objects.filter(
        staff__id=staff_id, claim_id=claim_id or ""
    ).first()
    if conversation is None:
        ClaimConversation.objects.create(
            staff=StaffProxy.objects.get(id=staff_id),
            claim_id=claim_id or "",
            messages=messages,
        )
    else:
        conversation.messages = messages
        conversation.save()


class ClaimsChatAgent(AgentPlugin):
    """Chat agent behind the claims chat application, in queue or claim mode."""

    tools = tools

    def _staff_id(self) -> str:
        # Queue mode needs a staff member for its scope, and claim mode needs the revenue
        # capability, which only a staff member earns, so every run has one.
        if not self.requester.staff_id:
            raise ValueError("ClaimsChatAgent needs a run a staff member started")
        return self.requester.staff_id

    def load_state(self, scope_key: str) -> AgentState:
        """Read the staff member's conversation for this run's claim, or for the queues."""
        messages = load_claims_conversation(self._staff_id(), self.subject.claim_id)
        return AgentState(data={"messages": messages})

    def system_prompt(self) -> str:
        """The instructions, with the mode this run is in."""
        if self.subject.claim_id:
            return SYSTEM_PROMPT + CLAIM_MODE.format(claim_id=self.subject.claim_id)
        return SYSTEM_PROMPT + QUEUE_MODE

    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict,
    ) -> AgentRunResult:
        """Answer the staff member's message, or explain that they lack revenue access."""
        messages = [
            *state.data["messages"],
            {"role": "user", "content": trigger_payload["user_message"]},
        ]
        if Capability.REVENUE not in self.capabilities:
            state.data["messages"] = [
                *messages,
                {"role": "assistant", "content": NO_REVENUE_ACCESS},
            ]
            return AgentRunResult(state=state)

        result = self.run_tool_loop(
            gateway, system=self.system_prompt(), messages=messages, max_turns=MAX_TURNS
        )
        state.data["messages"] = result.messages
        # Opaque identifiers only: logs leave the instance.
        log.info(
            f"ClaimsChatAgent: turn complete for claim_id={self.subject.claim_id} "
            f"({result.turns} LLM turn(s), {result.stopped}, {len(result.effects)} effect(s))"
        )
        return AgentRunResult(state=state, effects=result.effects)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """Persist the newest part of the conversation."""
        messages = window_messages(state.data["messages"], STORED_HISTORY_CHARS)
        _save_claims_conversation(self._staff_id(), self.subject.claim_id, messages)
