from typing import Any

from agent_runner_poc.agents.longitudinal_advisor_tools import tools as _registered_tools
from agent_runner_poc.agents.run_logging import RunLoggingMixin
from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, LLMGateway
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import ProtocolCurrent
from logger import log

# Used both in find_protocol_cards filters and in the user-message preamble
# so the agent has a clear handle on "these are mine vs. someone else's."
PLUGIN_NAME = "agent_runner_poc"

SYSTEM_PROMPT = (
    "You are a longitudinal care advisor reviewing a patient's just-completed "
    "encounter. Your job is to maintain a small set of protocol cards on the "
    "patient that represent open clinical recommendations from prior visits.\n\n"
    "On each run you see the existing protocol cards your plugin previously "
    "staged (in the user message). For each card, decide:\n"
    "- If the underlying issue was addressed this visit (the clinician acted, "
    "a recheck arrived, a med was changed), update the card with the same "
    "`card_key` and `status='satisfied'`.\n"
    "- If the recommendation no longer applies (patient declined, condition "
    "resolved unrelatedly), update with `status='not_relevant'`.\n"
    "- Otherwise leave it alone — it remains visible as `due`.\n\n"
    "Then identify NEW follow-up actions implied by what changed this visit. "
    "For each, call `add_or_update_protocol_card` with a fresh `card_key` "
    "(omit it and the SDK generates one), `status='due'`, `can_be_snoozed=true`,"
    "`feedback_enabled=true`, a short `title`, "
    "and a clinical-context `narrative`. Be conservative — three or fewer "
    "new cards per visit.\n\n"
    "When a recommendation maps cleanly to a discrete chart action (order a "
    "lab, order imaging, refer, prescribe, schedule a follow-up visit), attach "
    "a `commands` entry to the recommendation so the clinician can act in one "
    "click. Each command is `{type, context}` — type is the originate-command "
    "kind (labOrder, imagingOrder, refer, prescribe, followUp, assess, "
    "instruct, plan, stopMedication, diagnose, goal); context carries the "
    "command's args (e.g., for labOrder: `tests_order_codes`, "
    "`diagnosis_codes`). When the clinician clicks the recommendation's "
    "button, the platform stages the originated command as a draft for them "
    "to review and commit. Skip `commands` when the next step is judgment "
    "(discussion, monitoring) rather than a concrete order.\n\n"
    "Use the chart-read tools (find_conditions, find_lab_results, "
    "find_medications, find_tasks, etc.) to verify your reasoning before "
    "you act. When done, end your turn."
)

MAX_TURNS = 10


def _format_protocol_card_context(patient_id: str) -> str:
    """Build the human-readable preamble listing this plugin's existing cards.

    Includes every card staged by this plugin regardless of status — the agent
    decides whether to leave each alone, mark it satisfied, or update its
    narrative. Other plugins' cards are not surfaced (they're not ours to
    modify).
    """
    cards = list(
        ProtocolCurrent.objects.filter(
            patient__id=patient_id,
            plugin_name=PLUGIN_NAME,
        ).order_by("-created")
    )

    if not cards:
        return (
            "No protocol cards from prior visits. Identify new follow-up needs from this encounter."
        )

    lines: list[str] = [
        "Protocol cards staged by this plugin on prior visits "
        "(update via add_or_update_protocol_card with the same card_key):",
    ]
    for card in cards:
        lines.append(
            f"  - card_key={card.protocol_key!r} status={card.status!r} title={card.title!r}"
        )
        if card.narrative:
            lines.append(f"    narrative: {card.narrative}")
    return "\n".join(lines)


class LongitudinalCareAdvisor(RunLoggingMixin, AgentPlugin):
    """Reviews each locked encounter against the patient's open protocol cards.

    Uses the SDK's ProtocolCard surface (`add_or_update_protocol_card` +
    `find_protocol_cards`) for cross-visit tracking instead of a plugin-
    private Custom Data table. The card's stable `key` is the cross-run
    identifier; status updates flow through the same effect. The clinician
    sees and interacts with the cards in the chart UI.

    No durable state in AgentState — every cross-visit fact is queryable
    via ProtocolCurrent.
    """

    # Platform-scoped to the manifest's tools.allowed before run() fires.
    tools = _registered_tools

    def load_state(self, scope_key: str) -> AgentState:
        """No serialized state — durable state lives in ProtocolCurrent."""
        return AgentState()

    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict,
    ) -> AgentRunResult:
        """Brief the model with existing cards + drive a tool-use loop."""
        patient_id = trigger_payload["patient_id"]
        note_id = trigger_payload["note_id"]

        context_block = _format_protocol_card_context(patient_id)

        effects: list[Effect] = []
        tool_ctx: dict[str, Any] = {
            "patient_id": patient_id,
            "note_id": note_id,
            "effects": effects,
        }

        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                # No name or other identifiers: the tools are already scoped to
                # the patient, so the model needs only the task and the cards.
                "content": (
                    "The patient just had a visit complete (note locked). Review "
                    f"the chart for follow-up needs.\n\n{context_block}"
                ),
            }
        ]
        result = self.run_tool_loop(
            gateway, ctx=tool_ctx, system=SYSTEM_PROMPT, messages=messages, max_turns=MAX_TURNS
        )

        log.info(
            f"LongitudinalCareAdvisor loop complete for note {note_id}: {result.turns} LLM "
            f"turn(s), {result.stopped}, {len(effects)} effect(s) staged"
        )
        return AgentRunResult(state=state, effects=effects)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """No-op — durable state lives in ProtocolCurrent, not AgentState."""
        return None
