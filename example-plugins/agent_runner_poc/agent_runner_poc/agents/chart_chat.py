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

The full tool surface — clinical reads, task/banner/protocol writes,
and the originate-on-note commands (Plan/Prescribe/LabOrder/Diagnose/
Goal/Assessment/FollowUp/StopMedication) — comes from the SDK's
``standard_tools`` registry via ``tools.extend(standard_tools)`` in
chart_chat_tools.py. The manifest grants @clinical_reads,
@clinical_writes, @task_writes, and @clinical_alerts with no
exclusions.

For the SDK's originate-command tools to work in chat-style runs,
``respond()`` resolves the patient's current open note once per turn
via :func:`find_open_note_uuid_from_ctx` and stores the UUID on
``tool_ctx["note_id"]`` before tool dispatch. The SDK's default
``note_resolver`` reads that key — same shape triggered agents use.
"""

import json
from typing import Any, cast

from anthropic import Anthropic
from anthropic.types import TextBlock, ToolUseBlock

from agent_runner_poc.agents.chart_chat_tools import tools as _registered_tools
from agent_runner_poc.agents.run_logging import RunLoggingMixin
from agent_runner_poc.models.conversation import Conversation
from agent_runner_poc.models.proxy import PatientProxy
from canvas_sdk.agents import (
    AgentPlugin,
    AgentRunResult,
    AgentState,
    LLMGateway,
    find_open_note_uuid_from_ctx,
)
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import Patient
from logger import log

SYSTEM_PROMPT = (
    "You are a clinical assistant embedded in the chart of a single patient. "
    "A clinician is chatting with you to learn about this patient, reason "
    "through their care, and stage actions for the clinician to review.\n\n"
    "Tool families:\n"
    "- READ tools (`find_*`, `get_patient_demographics`) — searchable views "
    "of the patient's chart. Most return row IDs you can pass to write tools "
    "that need them (e.g., `originate_assessment` needs a condition_id from "
    "`find_conditions`; `originate_stop_medication` needs a medication_id "
    "from `find_medications`).\n"
    "- TASK tools (`create_task`, `update_task`, `add_task_comment`) — "
    "create follow-up work or close/comment on existing tasks. Use for "
    "actions the clinician should take later that don't fit a chart command "
    "(call patient, review external records).\n"
    "- MESSAGE tools (`find_messages`, `originate_message`) — read the "
    "patient ↔ staff message history, or draft a new message from the "
    "requesting staff to this patient. Drafts NEVER send — they sit in "
    "the staff's outbox for review.\n"
    "- COMPOSITION tools (`generate_chart_summary`, "
    "`generate_pre_visit_brief`) — delegate to focused sub-agents. "
    "`generate_chart_summary` returns a concise narrative of the patient's "
    "chart; you decide what to do with the text. "
    "`generate_pre_visit_brief` fans out to four parallel sub-agents "
    "across multiple chart domains and returns their summaries for you "
    "to synthesize. Faster and more focused than calling find_* tools "
    "yourself.\n"
    "- BANNER + PROTOCOL tools (`add_banner_alert`, `remove_banner_alert`, "
    "`find_banner_alerts`, `add_or_update_protocol_card`) — surface "
    "clinically meaningful state. Banners are short visual flags; protocol "
    "cards are richer CDS surfaces with title + narrative + recommended "
    "actions. Use sparingly — don't duplicate flags that already exist; "
    "call `find_banner_alerts` first if you're unsure.\n"
    "- ORIGINATE tools (`originate_prescribe_medication`, "
    "`originate_lab_order`, `originate_goal`, `originate_assessment`, "
    "`originate_follow_up`, `originate_stop_medication`) — stage a draft "
    "command on the patient's current open note for clinician review. "
    "NEVER commits — the clinician reviews/edits/commits in the chart UI. "
    "Use only when the clinician explicitly asks to do that thing.\n\n"
    "Selection guidance:\n"
    "- Prescribing → `originate_prescribe_medication`, NOT `create_task`.\n"
    "- Stopping a med → `originate_stop_medication`, NOT a task or banner.\n"
    "- Recheck/follow-up visit → `originate_follow_up`.\n"
    "- A clinical concern the clinician should notice on the next visit "
    "but doesn't have a discrete task → banner alert or protocol card.\n"
    "- Replying to or messaging the patient (e.g. 'draft a reply about "
    "her A1c', 'message the patient that the lab is normal') → "
    "`originate_message`. ALWAYS pull the recent thread with "
    "`find_messages(from_patient_only=true)` first so the draft "
    "addresses what the patient actually asked. Write in plain "
    "English at a patient-reading level; sign off as the clinician if "
    "appropriate. Drafts NEVER send — the clinician hits Send.\n"
    "- Pre-visit prep ('what do I need to know about this patient "
    "before their appointment', 'give me a brief', 'summarize this "
    "patient') → `generate_pre_visit_brief`. Read all four returned "
    "domain summaries, then write a unified brief in plain prose for "
    "the clinician. Don't just paste the sub-agent output — your job "
    "is to synthesize.\n"
    "- Drafting a chart-review note ('write up a review note for the "
    "recent labs', 'draft a chart-review summary') → first call "
    "`generate_chart_summary` to get the narrative, then "
    "`originate_review_note` with that narrative. Two prerequisite reads "
    "for the note: `find_note_types(category='review')` for the "
    "customer's review note type UUID, and `find_practice_locations` to "
    "pick a location (default to the first active one if the clinician "
    "doesn't specify). NEVER commits — the note + plan command land as "
    "a draft for the clinician to review, edit, and sign.\n"
    "- Summarizing the patient inline in chat ('what's going on with "
    "this patient', 'give me the rundown') → `generate_chart_summary` "
    "alone; paste the returned narrative into your reply.\n"
    "- Ordering labs ('order a lipid panel', 'add a fasting glucose') → "
    "three-step flow because the agent needs to discover real codes: "
    "(1) `find_lab_partners(active_only=true, electronic_ordering_only=true)` "
    "and pick one (default to the first if the clinician doesn't "
    "specify); (2) `find_lab_partner_tests(lab_partner_id=<id>, "
    "search='glucose')` to get the real order codes; (3) "
    "`originate_lab_order(lab_partner=<id>, tests_order_codes=[<order_code>, ...])`. "
    "Don't guess order codes — the command validator rejects unknown "
    "ones.\n\n"
    "Chart navigation:\n"
    "When the clinician asks to navigate to a specific note ('open the "
    "note where I first diagnosed X', 'show me the visit from last "
    "Tuesday', 'scroll to where we discussed Y'), find the target note "
    "via `find_notes` / `find_conditions` / `get_note_content` as needed, "
    "then include `[[scroll-to-note:<dbid>]]` in your reply — the `dbid` "
    "field on the matching note row (an integer; NOT the UUID `id` "
    "field). The chat UI strips the marker and scrolls the chart to that "
    "note, auto-loading more pages and expanding it if collapsed. Use at "
    "most one marker per reply.\n\n"
    "Questionnaire scoring & interpretation:\n"
    "`find_questionnaire_responses` returns each Interview's per-question "
    "answers including `response_value` — the option's underlying scale "
    "value (often numeric, e.g. '1'-'4' for Likert). For instruments "
    "where the scoring is obvious (PHQ-9 sums to 0-27, Stress is 1-4 "
    "per item) you can summarize or chart `response_value` directly. "
    "BUT — the value may be non-numeric, or the customer's scale may "
    "not match the canonical instrument's. If there's any ambiguity "
    "(repeated values across distinct options, non-numeric strings, an "
    "unfamiliar instrument), DO NOT silently invent a numeric mapping. "
    'Tell the clinician what you see, propose a conversion (e.g. "map '
    "'Very much'→4, 'Not at all'→0, treat higher as worse — is that "
    'right?"), and wait for sign-off before charting or quoting the '
    "result as a score. The model is the interpreter; the clinician "
    "owns the interpretation.\n\n"
    "Visualizations:\n"
    "When the clinician asks for a chart/graph/plot ('show me weight "
    "over time', 'plot BPs since January', 'histogram of A1c'), pull "
    "the underlying data with `find_vitals` / `find_lab_results` / etc. "
    "(use `name_contains` to scope to a single measurement; bump `limit` "
    "if you need a longer history), then embed a Vega-Lite v5 spec in "
    "a fenced code block in your reply. Inline the actual data values "
    "in the spec's `data.values` array — don't reference URLs. Example:\n"
    "```vega-lite\n"
    '{"$schema":"https://vega.github.io/schema/vega-lite/v5.json",'
    '"width":420,"height":240,'
    '"data":{"values":[{"date":"2024-01-15","weight":85.2},'
    '{"date":"2024-04-02","weight":83.7},{"date":"2024-07-19","weight":82.4}]},'
    '"mark":{"type":"line","point":true},'
    '"encoding":{"x":{"field":"date","type":"temporal","title":"Date"},'
    '"y":{"field":"weight","type":"quantitative","title":"Weight (kg)"}}}\n'
    "```\n"
    "Briefly comment on what the chart shows in plain text before the "
    "fence. Keep specs minimal — no transforms or multi-layer views "
    "unless explicitly requested. One chart per reply unless asked.\n\n"
    "For discussion or summary, stay read-only. Use write tools only when "
    "the clinician explicitly asks. Keep responses concise and clinically "
    "focused. Plain text only — no markdown headings."
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


class ChartChatAgent(RunLoggingMixin, AgentPlugin):
    """Chat agent backing the in-chart conversation surface.

    Snapshot state pattern: the full message history lives in a single
    :class:`Conversation` row and is loaded/mutated/saved as a unit.
    Different from the LongitudinalCareAdvisor (event-sourced rows) and
    ChartSummary (no state at all) — same SDK base class, three storage
    models depending on what the agent actually needs.
    """

    # The platform scopes this to the manifest's tools.allowed before
    # run() fires; `self.tools.definitions()` and `self.tools.execute(...)`
    # then see only the authorized subset (doc §6.7 enforcement seam).
    tools = _registered_tools

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
        # staff_id rides through the trigger_payload from ChartChatAPI's
        # session-auth header. Stamped onto tool_ctx so message-write tools
        # (originate_message) can attribute drafts to the requesting staff
        # without the model having to know who's asking. Optional —
        # background/triggered invocations may not have a staff in scope.
        staff_id = trigger_payload.get("staff_id")

        # Working messages list — mutate in place, persist at end via save_state.
        messages: list[dict[str, Any]] = list(state.data.get("messages") or [])
        messages.append({"role": "user", "content": user_message})

        # Shared context for the tool dispatcher. The effects accumulator
        # collects originated commands / Tasks from write tools (create_task,
        # originate_prescribe_medication, etc.); the platform dispatches each
        # exactly once after run() returns via AgentRunResult.effects.
        #
        # Resolve the patient's current open note once per turn and stash the
        # UUID on ctx. The SDK's originate-command tools read ctx["note_id"]
        # by default — chat-style agents are responsible for populating it;
        # triggered agents get it from their trigger payload. If no open
        # note exists, the helper returns the structured no-note error
        # individually per tool call so the model can tell the clinician.
        effects: list[Effect] = []
        tool_ctx: dict[str, Any] = {
            "patient_id": patient_id,
            "staff_id": staff_id,
            "effects": effects,
            # Stamp the gateway + parent tools registry so composition
            # tools like `generate_pre_visit_brief` can spawn sub-agents
            # via run_subagents(). Sub-agents share this same ctx so
            # their write effects flow into `effects`, and their tool
            # subset is scoped from `parent_tools`.
            "gateway": gateway,
            "parent_tools": self.tools,
        }
        tool_ctx["note_id"] = find_open_note_uuid_from_ctx(tool_ctx)

        client = Anthropic(api_key=gateway.api_key)
        final_text = ""

        for turn in range(MAX_TURNS):
            # Plain assignment — RestrictedPython forbids augmented attribute
            # assignment (`self.x += 1`) in the sandbox.
            self._llm_turn_count = self._llm_turn_count + 1
            response = client.messages.create(
                model=gateway.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                # `self.tools` is the manifest-scoped registry — already
                # filtered to the allowlist when run() fired.
                tools=cast(Any, self.tools.definitions()),
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

            # 'tool_use' is the normal dispatch case. 'max_tokens' means the
            # model was cut off mid-response — any complete tool_use blocks
            # in response.content are still valid; dispatch them and let the
            # next turn pick up.
            tool_use_blocks = [b for b in response.content if isinstance(b, ToolUseBlock)]
            if response.stop_reason in ("tool_use", "max_tokens") and tool_use_blocks:
                if response.stop_reason == "max_tokens":
                    log.warning(
                        f"ChartChatAgent turn={turn} hit max_tokens with "
                        f"{len(tool_use_blocks)} pending tool_use block(s); dispatching anyway"
                    )
                tool_results: list[dict[str, Any]] = []
                for block in tool_use_blocks:
                    try:
                        result = self.tools.execute(
                            block.name,
                            dict(block.input),
                            ctx=tool_ctx,
                        )
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
