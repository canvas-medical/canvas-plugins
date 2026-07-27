import json
from typing import Any, cast

from anthropic import Anthropic
from anthropic.types import ToolUseBlock

from agent_runner_poc.agents.longitudinal_advisor_tools import tools as _registered_tools
from agent_runner_poc.agents.run_logging import RunLoggingMixin
from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, LLMGateway
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import Patient, ProtocolCurrent
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

        patient = Patient.objects.get(id=patient_id)
        context_block = _format_protocol_card_context(patient_id)

        effects: list[Effect] = []
        tool_ctx: dict[str, Any] = {
            "patient_id": patient_id,
            "note_id": note_id,
            "effects": effects,
        }

        client = Anthropic(api_key=gateway.api_key)
        messages: list[dict] = [
            {
                "role": "user",
                "content": (
                    f"Patient {patient.first_name} {patient.last_name} just had "
                    f"a visit complete (note locked). Review the chart for "
                    f"follow-up needs.\n\n{context_block}"
                ),
            }
        ]

        for turn in range(MAX_TURNS):
            self._llm_turn_count = self._llm_turn_count + 1
            response = client.messages.create(
                model=gateway.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=cast(Any, self.tools.definitions()),
                messages=cast(Any, messages),
            )
            log.info(
                f"LongitudinalCareAdvisor turn={turn} stop_reason={response.stop_reason} "
                f"blocks={[b.type for b in response.content]}"
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                break

            # 'tool_use' is the normal dispatch case. 'max_tokens' means the
            # model was cut off mid-response — any complete tool_use blocks
            # in response.content are still valid; dispatch them and let the
            # next turn pick up. Without this branch, a max_tokens turn with
            # pending tool_use blocks silently drops them (the original cause
            # of "0 effects staged" despite the model intending to act).
            tool_use_blocks = [b for b in response.content if isinstance(b, ToolUseBlock)]
            if response.stop_reason in ("tool_use", "max_tokens") and tool_use_blocks:
                if response.stop_reason == "max_tokens":
                    log.warning(
                        f"LongitudinalCareAdvisor turn={turn} hit max_tokens with "
                        f"{len(tool_use_blocks)} pending tool_use block(s); dispatching anyway"
                    )
                tool_results: list[dict] = []
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
                        log.exception(f"LongitudinalCareAdvisor: tool {block.name!r} raised")
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

            log.warning(
                f"LongitudinalCareAdvisor: unexpected stop_reason={response.stop_reason!r}; bailing"
            )
            break
        else:
            log.warning(
                f"LongitudinalCareAdvisor: hit MAX_TURNS={MAX_TURNS} without end_turn; "
                "returning whatever was staged"
            )

        log.info(
            f"LongitudinalCareAdvisor loop complete for note {note_id}; "
            f"{len(effects)} effect(s) staged"
        )
        return AgentRunResult(state=state, effects=effects)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """No-op — durable state lives in ProtocolCurrent, not AgentState."""
        return None
