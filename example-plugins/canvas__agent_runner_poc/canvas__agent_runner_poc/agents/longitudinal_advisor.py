import json
from typing import Any

from canvas__agent_runner_poc.agents.longitudinal_advisor_tools import tools as _registered_tools
from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, LLMGateway, ToolRegistry
from logger import log

# Scopes load_state's find_protocol_cards to this plugin's own cards: the other
# plugins' cards are not this agent's to update.
PLUGIN_NAME = "canvas__agent_runner_poc"

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


# The most of this plugin's cards a run reviews: find_protocol_cards' own ceiling.
MAX_CARDS = 100


def _cards_message(cards: list[dict[str, Any]]) -> str:
    """The user message: the task, and this plugin's cards from earlier visits."""
    task = (
        "The patient just had a visit complete (note locked). Review the chart for follow-up needs."
    )
    if not cards:
        return (
            f"{task}\n\nNo protocol cards from prior visits. Identify new follow-up needs "
            "from this encounter."
        )
    return (
        f"{task}\n\nProtocol cards staged by this plugin on prior visits, as "
        "find_protocol_cards returns them (update one via add_or_update_protocol_card "
        f"with its protocol_key as card_key):\n{json.dumps(cards, indent=1)}"
    )


class LongitudinalCareAdvisor(AgentPlugin):
    """Reviews each locked encounter against the patient's open protocol cards.

    Uses the SDK's ProtocolCard surface (`add_or_update_protocol_card` +
    `find_protocol_cards`) for cross-visit tracking instead of a plugin-
    private Custom Data table. The card's stable `key` is the cross-run
    identifier; status updates flow through the same effect. The clinician
    sees and interacts with the cards in the chart UI.

    Its state is the cards: ``load_state`` reads them, and the run's card effects are
    the only writes, so ``save_state`` has nothing to keep.
    """

    # Platform-scoped to the manifest's tools.allowed before run() fires.
    tools = _registered_tools

    def load_state(self, scope_key: str) -> AgentState:
        """The protocol cards this plugin staged on the patient on earlier visits.

        Read through find_protocol_cards, the tool the model also has, so the cards come
        from one query in one shape and within the run's patient and tool grant. Runs on
        the patient happen one at a time, so the last run's cards are applied by now.
        """
        tools = self.tools or ToolRegistry()
        cards = tools.execute(
            "find_protocol_cards",
            {"plugin_name": PLUGIN_NAME, "limit": MAX_CARDS},
            ctx=self.tool_context(),
        )
        return AgentState(data={"cards": cards})

    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict,
    ) -> AgentRunResult:
        """Brief the model with this plugin's cards, then drive the tool loop."""
        # No name or other identifiers: the tools are already scoped to the patient, so
        # the model needs only the task and the cards.
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": _cards_message(state.data.get("cards") or [])}
        ]
        result = self.run_tool_loop(
            gateway, system=SYSTEM_PROMPT, messages=messages, max_turns=MAX_TURNS
        )

        log.info(
            f"LongitudinalCareAdvisor loop complete for note {self.subject.note_id}: "
            f"{result.turns} LLM turn(s), {result.stopped}, {len(result.effects)} effect(s) staged"
        )
        return AgentRunResult(state=state, effects=result.effects)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """Nothing to write: the cards change only through the run's effects."""
        return None
