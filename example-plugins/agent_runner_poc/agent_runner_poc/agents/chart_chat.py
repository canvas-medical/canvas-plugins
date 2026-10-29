"""ChartChatAgent — user-initiated chat agent for the patient chart.

Demonstrates the snapshot state pattern from doc §6.12:
- ``load_state`` reads the patient's :class:`Conversation` row and pulls the
  full message history into ``state.data["messages"]``.
- ``run()`` appends the clinician's new message and answers it with
  :meth:`AgentPlugin.run_tool_loop`, which returns the history with the new
  turns appended.
- ``save_state`` writes the updated message list back to the same row.

Dispatched via the standard ``RunAgent`` path: the chat UI's POST
handler emits a :class:`RunAgentEffect` scoped to the patient and clinician,
with ``user_message`` in ``trigger_payload``, the home-app ``RunAgentEffectInterpreter`` enqueues
a Celery task, and the plugin-runner's ``RunAgent`` RPC drives the
lifecycle, one run at a time per ``scope_key``. The UI polls
``/chart-chat-history`` to surface the assistant turn when it lands.

The full tool surface — clinical reads, task/banner/protocol writes,
and the originate-on-note commands (Plan/Prescribe/LabOrder/Diagnose/
Goal/Assessment/FollowUp/StopMedication) — comes from the SDK's
``standard_tools`` registry via ``tools.extend(standard_tools)`` in
chart_chat_tools.py. The manifest grants @clinical_reads,
@clinical_writes, @task_writes, and @clinical_alerts with no
exclusions.

For the SDK's originate-command tools to work in chat-style runs,
``run()`` resolves the clinician's open note once per run via
:func:`find_open_note_uuid_from_ctx` and stores its UUID on
``tool_ctx["note_id"]``, the key the SDK's default ``note_resolver`` reads.
"""

from typing import Any

from agent_runner_poc.agents.chart_chat_tools import tools as _registered_tools
from agent_runner_poc.agents.run_logging import RunLoggingMixin
from agent_runner_poc.models.conversation import Conversation
from agent_runner_poc.models.proxy import PatientProxy, StaffProxy
from canvas_sdk.agents import (
    AgentPlugin,
    AgentRunResult,
    AgentState,
    LLMGateway,
    find_open_note_uuid_from_ctx,
)
from canvas_sdk.effects import Effect
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

SCOPE_PREFIX = "agent_runner_poc:chart_chat"


def chart_chat_scope_key(patient_id: str, staff_id: str) -> str:
    """The scope of one clinician's conversation about one patient."""
    return f"{SCOPE_PREFIX}:patient:{patient_id}:staff:{staff_id}"


def _scope_ids(scope_key: str) -> tuple[str, str]:
    """The patient and staff ids a :func:`chart_chat_scope_key` names."""
    _, patient_id, _, staff_id = scope_key.removeprefix(f"{SCOPE_PREFIX}:").split(":")
    return patient_id, staff_id


def load_conversation_messages(patient_id: str, staff_id: str) -> list[dict[str, Any]]:
    """Read a clinician's message history about a patient from Conversation Custom Data."""
    conversation = Conversation.objects.filter(patient__id=patient_id, staff__id=staff_id).first()
    if conversation is None:
        return []
    return list(conversation.messages or [])


def _save_conversation_messages(
    patient_id: str,
    staff_id: str,
    messages: list[dict[str, Any]],
) -> None:
    """Persist the updated message history; create the Conversation row on first save."""
    conversation = Conversation.objects.filter(patient__id=patient_id, staff__id=staff_id).first()
    if conversation is None:
        Conversation.objects.create(
            patient=PatientProxy.objects.get(id=patient_id),
            staff=StaffProxy.objects.get(id=staff_id),
            messages=messages,
        )
    else:
        conversation.messages = messages
        conversation.save()


class ChartChatAgent(RunLoggingMixin, AgentPlugin):
    """Chat agent backing the in-chart conversation surface.

    Snapshot state pattern: the clinician's full message history lives in a
    single :class:`Conversation` row and is loaded/mutated/saved as a unit,
    where the LongitudinalCareAdvisor keeps its state in the chart.
    """

    # The platform scopes this to the manifest's tools.allowed before
    # run() fires; `self.tools.definitions()` and `self.tools.execute(...)`
    # then see only the authorized subset (doc §6.7 enforcement seam).
    tools = _registered_tools

    def load_state(self, scope_key: str) -> AgentState:
        """Read the clinician's conversation snapshot for this patient.

        ``scope_key`` is a :func:`chart_chat_scope_key`, which names both.
        """
        patient_id, staff_id = _scope_ids(scope_key)
        return AgentState(
            data={
                "patient_id": patient_id,
                "staff_id": staff_id,
                "messages": load_conversation_messages(patient_id, staff_id),
            }
        )

    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict,
    ) -> AgentRunResult:
        """Answer the clinician's new message through the tool-use loop."""
        # The patient and clinician come from the scope (via load_state), the same
        # place save_state writes to, so the chart the tools read and the
        # conversation saved can't diverge. The clinician goes on the tool context
        # so message drafts are attributed to them and originate tools use their
        # open note.
        effects: list[Effect] = []
        tool_ctx: dict[str, Any] = {
            "patient_id": state.data["patient_id"],
            "staff_id": state.data["staff_id"],
            "effects": effects,
            # Composition tools (generate_pre_visit_brief, ...) run sub-agents with
            # the run's gateway and a subset of this agent's granted tools.
            "gateway": gateway,
            "parent_tools": self.tools,
        }
        tool_ctx["note_id"] = find_open_note_uuid_from_ctx(tool_ctx)

        messages = [
            *state.data["messages"],
            {"role": "user", "content": trigger_payload["user_message"]},
        ]
        result = self.run_tool_loop(
            gateway, ctx=tool_ctx, system=SYSTEM_PROMPT, messages=messages, max_turns=MAX_TURNS
        )
        state.data["messages"] = result.messages

        # Opaque identifiers only: logs leave the instance, so no names or chart content.
        log.info(
            f"ChartChatAgent: turn complete for patient_id={state.data['patient_id']} "
            f"({result.turns} LLM turn(s), {result.stopped}, {len(effects)} effect(s))"
        )
        return AgentRunResult(state=state, effects=effects)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """Persist the updated message snapshot back to the Conversation row."""
        messages: list[dict[str, Any]] = state.data["messages"]
        _save_conversation_messages(state.data["patient_id"], state.data["staff_id"], messages)
