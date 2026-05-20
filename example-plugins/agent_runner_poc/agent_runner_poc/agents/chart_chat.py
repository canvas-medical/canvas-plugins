"""ChartChatAgent — user-initiated chat agent for the patient chart.

Demonstrates the snapshot state pattern from doc §6.12:
- ``load_state`` reads the patient's :class:`Conversation` row and pulls the
  full message history into ``state.data["messages"]``.
- ``run()`` appends the user's new message, drives a tool-use loop over
  the chart, appends the assistant's response, and stashes the text in
  ``state.data["last_response"]``.
- ``save_state`` writes the updated message list back to the same row.

Dispatched via the standard ``RunAgent`` path: the chat UI's POST
handler emits a :class:`RunAgentEffect` with ``{patient_id, user_message}``
in ``trigger_payload``, the home-app ``RunAgentEffectInterpreter`` enqueues
a Celery task, and the plugin-runner's ``RunAgent`` RPC drives the
lifecycle inside the per-``scope_key`` ``agent_lock``. The UI polls
``/chart-chat-history`` to surface the assistant turn when it lands.

For phase 1 the agent has read tools only. Effect tools could be added
later (e.g. ``propose_task`` so the chat can stage actions inline).
"""

import json
from typing import Any, cast

from anthropic import Anthropic
from anthropic.types import TextBlock, ToolUseBlock

from agent_runner_poc.agents.chart_chat_tools import tools
from agent_runner_poc.models.conversation import Conversation
from agent_runner_poc.models.proxy import PatientProxy
from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, LLMGateway
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import Patient
from logger import log

SYSTEM_PROMPT = (
    "You are a clinical assistant embedded in the chart of a single patient. "
    "A clinician is chatting with you to learn about this patient, reason "
    "through their care, and stage actions for the clinician to review. You "
    "have read tools (demographics, conditions with onset dates, medications, "
    "recent labs, recent assessments) and write tools (create_task; "
    "originate—but never commit—prescriptions, lab orders, and diagnoses). "
    "Originated commands land in draft form on the patient's current open "
    "note for the clinician to review, edit, and commit; you never commit "
    "anything yourself. Use the write tools only when the clinician "
    "explicitly asks; for discussion or summary, stay read-only. Keep "
    "responses concise and clinically focused. Plain text only — no "
    "markdown headings."
)

MAX_TURNS = 8


def _load_conversation_messages(patient_id: str) -> list[dict[str, Any]]:
    """Read the patient's existing message history from Conversation Custom Data."""
    conversation = Conversation.objects.filter(patient__id=patient_id).first()
    if conversation is None:
        return []
    return list(conversation.messages or [])


def _save_conversation_messages(patient_id: str, messages: list[dict[str, Any]]) -> None:
    """Persist the updated message history; create the Conversation row on first save."""
    patient = PatientProxy.objects.get(id=patient_id)
    conversation = Conversation.objects.filter(patient__id=patient_id).first()
    if conversation is None:
        Conversation.objects.create(patient=patient, messages=messages)
    else:
        conversation.messages = messages
        conversation.save()


def _serialize_assistant_blocks(content: Any) -> list[dict[str, Any]]:
    """Convert Anthropic SDK block objects into JSON-serializable dicts.

    ``response.content`` from the Anthropic SDK is a list of typed block
    objects (TextBlock, ToolUseBlock, etc.). We round-trip them through the
    SDK's ``.model_dump()`` representation so the persisted history is plain
    JSON and re-loadable into the next turn's messages list.
    """
    serialized: list[dict[str, Any]] = []
    for block in content:
        # Anthropic blocks are pydantic models; model_dump produces JSON-safe dicts.
        serialized.append(block.model_dump())
    return serialized


class ChartChatAgent(AgentPlugin):
    """Chat agent backing the in-chart conversation surface.

    Snapshot state pattern: the full message history lives in a single
    :class:`Conversation` row and is loaded/mutated/saved as a unit.
    Different from the LongitudinalCareAdvisor (event-sourced rows) and
    ChartSummary (no state at all) — same SDK base class, three storage
    models depending on what the agent actually needs.
    """

    def load_state(self, scope_key: str) -> AgentState:
        """Read the conversation snapshot for this patient.

        ``scope_key`` is ``agent_runner_poc:chart_chat:patient:{patient_id}``;
        we extract the patient_id from the trailing segment.
        """
        patient_id = scope_key.rsplit(":", 1)[-1]
        return AgentState(
            data={
                "patient_id": patient_id,
                "messages": _load_conversation_messages(patient_id),
                "last_response": "",
            }
        )

    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict,
    ) -> AgentRunResult:
        """Append the new user message, run the tool-use loop, capture the response."""
        patient_id = trigger_payload["patient_id"]
        user_message = trigger_payload["user_message"]

        # Working messages list — mutate in place, persist at end via save_state.
        messages: list[dict[str, Any]] = list(state.data.get("messages") or [])
        messages.append({"role": "user", "content": user_message})

        # Shared context for the tool dispatcher. The effects accumulator
        # collects originated commands / Tasks from write tools (create_task,
        # originate_prescribe_medication, etc.); the platform dispatches each
        # exactly once after run() returns via AgentRunResult.effects.
        effects: list[Effect] = []
        tool_ctx: dict[str, Any] = {"patient_id": patient_id, "effects": effects}

        client = Anthropic(api_key=gateway.api_key)
        final_text = ""

        for turn in range(MAX_TURNS):
            response = client.messages.create(
                model=gateway.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=cast(Any, tools.definitions()),
                messages=cast(Any, messages),
            )
            log.info(
                f"ChartChatAgent turn={turn} stop_reason={response.stop_reason} "
                f"blocks={[b.type for b in response.content]}"
            )

            # Persist the assistant turn into the message history before
            # deciding what to do next. Serialize blocks → dicts so the
            # next load_state can re-feed them to messages.create unchanged.
            messages.append(
                {"role": "assistant", "content": _serialize_assistant_blocks(response.content)}
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if isinstance(block, TextBlock):
                        final_text = block.text.strip()
                        break
                break

            if response.stop_reason == "tool_use":
                tool_results: list[dict[str, Any]] = []
                for block in response.content:
                    if not isinstance(block, ToolUseBlock):
                        continue
                    try:
                        result = tools.execute(block.name, dict(block.input), ctx=tool_ctx)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result, default=str),
                            }
                        )
                    except Exception as exc:
                        log.exception(f"ChartChatAgent: tool {block.name!r} raised")
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Tool execution failed: {exc!s}",
                                "is_error": True,
                            }
                        )
                messages.append({"role": "user", "content": tool_results})
                continue

            log.warning(f"ChartChatAgent: unexpected stop_reason={response.stop_reason!r}; bailing")
            break
        else:
            log.warning(
                f"ChartChatAgent: hit MAX_TURNS={MAX_TURNS} without end_turn; "
                "returning whatever text was last produced"
            )

        # Update the state object so save_state persists the new messages
        # and the SimpleAPI caller can read last_response off result.state.
        state.data["messages"] = messages
        state.data["last_response"] = final_text or "(no response)"

        # Resolve the patient's display name once for the log line.
        patient = Patient.objects.get(id=patient_id)
        log.info(
            f"ChartChatAgent: turn complete for {patient.first_name} {patient.last_name} "
            f"({len(messages)} total messages)"
        )

        return AgentRunResult(state=state, effects=effects)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """Persist the updated message snapshot back to the Conversation row."""
        patient_id: str = state.data["patient_id"]
        messages: list[dict[str, Any]] = state.data["messages"]
        _save_conversation_messages(patient_id, messages)
