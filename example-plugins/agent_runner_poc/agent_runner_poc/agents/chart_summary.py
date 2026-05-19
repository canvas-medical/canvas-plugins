from anthropic import Anthropic
from anthropic.types import TextBlock

from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, LLMGateway
from canvas_sdk.commands import PlanCommand
from canvas_sdk.v1.data import Patient
from logger import log

SYSTEM_PROMPT = (
    "You are a clinical documentation assistant. Draft a concise (<=3 sentences) "
    "Plan-section narrative for a follow-up encounter. Return the narrative text "
    "only — no preamble, no headings, no markdown."
)


class ChartSummary(AgentPlugin):
    """Drafts a Plan command after a note is locked. PoC scope: no persisted state."""

    def load_state(self, scope_key: str) -> AgentState:
        """Single-shot agent — no prior state to load."""
        return AgentState()

    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict,
    ) -> AgentRunResult:
        """Call Anthropic once with the patient's name and originate a Plan command."""
        note_id = trigger_payload["note_id"]
        patient = Patient.objects.get(id=trigger_payload["patient_id"])

        user_message = (
            f"A note for patient {patient.first_name} {patient.last_name} was just "
            "locked. Draft a brief Plan narrative for the next encounter."
        )

        client = Anthropic(api_key=gateway.api_key)
        response = client.messages.create(
            model=gateway.model,
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        first_block = response.content[0]
        if not isinstance(first_block, TextBlock):
            log.error(
                f"ChartSummary: unexpected non-text content block "
                f"{type(first_block).__name__!r}; skipping originate"
            )
            return AgentRunResult(state=state, effects=[])
        narrative = first_block.text.strip()
        log.info(f"ChartSummary draft for note {note_id}: {narrative!r}")

        plan_effect = PlanCommand(note_uuid=note_id, narrative=narrative).originate()
        return AgentRunResult(state=state, effects=[plan_effect])

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """Single-shot agent — nothing to persist."""
        return None
