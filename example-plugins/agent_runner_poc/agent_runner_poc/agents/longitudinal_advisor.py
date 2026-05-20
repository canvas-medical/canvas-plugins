import json
from typing import Any, cast

from anthropic import Anthropic
from anthropic.types import ToolUseBlock

from agent_runner_poc.agents.longitudinal_advisor_tools import tools
from agent_runner_poc.agents.run_logging import RunLoggingMixin
from agent_runner_poc.models.recommendation import Recommendation
from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, LLMGateway
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import LabValue, Patient, Task
from logger import log

SYSTEM_PROMPT = (
    "You are a longitudinal care advisor reviewing a patient's just-completed "
    "encounter against follow-up recommendations from prior visits. The user "
    "message tells you which of your prior recommendations are still open and "
    "which were recently addressed; you also have read tools to inspect the "
    "current chart (conditions, recent labs, medications).\n\n"
    "Your job:\n"
    "1. Decide whether each open recommendation should be re-raised this visit "
    "or marked as no-longer-relevant. (For now, just don't re-raise the "
    "obviously-still-open ones — they resurface automatically until acted on.)\n"
    "2. Identify NEW follow-up actions implied by what changed at this visit.\n"
    "3. For each NEW recommendation, call `propose_recommendation` once. "
    "Choose category carefully: `task` for actions that need human follow-up "
    '("discuss adherence at next visit"); `follow_up_lab` with `proxy_data.'
    "loinc` for lab rechecks; `none` only when no automated verification is "
    "possible.\n\n"
    "Be conservative. Three or fewer new recommendations per visit. Concise "
    "narratives (<=200 chars). After your last `propose_recommendation` "
    "call, end your turn."
)

MAX_TURNS = 10

# Recently-addressed recommendations to surface as context (so the agent can
# acknowledge follow-through without re-flagging).
RECENTLY_ADDRESSED_LIMIT = 5


def _verify_open_recommendations(patient_id: str) -> None:
    """For each open recommendation, run its proxy verifier and update status.

    Mutates Recommendation rows in place; does not return anything. Called
    once at the start of every advisor run so the agent reasons against an
    up-to-date picture.

    Proxy semantics:
    - ``"task"``: Looks up the paired Task by ``proxy_data["task_id"]``;
      marks the recommendation addressed if the Task is COMPLETED.
    - ``"follow_up_lab"``: Looks for a committed LabValue with a coding code
      matching ``proxy_data["loinc"]`` from a report dated >= the
      recommendation's ``created`` timestamp.
    - ``"none"``: No automatic verification; the only way these get marked
      addressed is via the paired Task being completed (same as ``"task"``,
      but without the dedicated category).
    """
    open_recs = Recommendation.objects.filter(patient__id=patient_id, status="open")
    for rec in open_recs:
        proxy_data = rec.proxy_data or {}
        if rec.category in {"task", "none"}:
            task_id = proxy_data.get("task_id")
            if not task_id:
                continue
            task = Task.objects.filter(id=task_id).first()
            if task is None:
                continue
            if task.status == "COMPLETED":
                rec.status = "addressed"
                rec.status_reason = f"task {task_id} completed at {task.modified.isoformat()}"
                rec.save()
        elif rec.category == "follow_up_lab":
            loinc = proxy_data.get("loinc")
            if not loinc:
                continue
            matching = LabValue.objects.filter(
                report__patient__id=patient_id,
                report__junked=False,
                report__original_date__gte=rec.flagged_at,
                codings__code=loinc,
            ).exists()
            if matching:
                rec.status = "addressed"
                rec.status_reason = f"matching lab for loinc={loinc} received"
                rec.save()


def _format_recommendation_context(patient_id: str) -> str:
    """Build the human-readable preamble that primes the agent's reasoning.

    Includes open recommendations from prior visits (with their flagged date
    and category) and a short tail of recently-addressed ones (so the agent
    can acknowledge progress without re-flagging things the clinician just
    did).
    """
    open_recs = list(
        Recommendation.objects.filter(patient__id=patient_id, status="open").order_by("-flagged_at")
    )
    addressed = list(
        Recommendation.objects.filter(patient__id=patient_id, status="addressed").order_by(
            "-status_updated_at"
        )[:RECENTLY_ADDRESSED_LIMIT]
    )

    lines: list[str] = []
    if open_recs:
        lines.append("Open recommendations from prior visits (do not re-propose):")
        for rec in open_recs:
            lines.append(
                f"  - [{rec.category}] {rec.narrative} "
                f"(flagged {rec.flagged_at.date().isoformat()})"
            )
    else:
        lines.append("No open recommendations from prior visits.")

    if addressed:
        lines.append("")
        lines.append("Recently addressed (informational, do not re-propose):")
        for rec in addressed:
            lines.append(
                f"  - [{rec.category}] {rec.narrative} — {rec.status_reason or 'addressed'}"
            )

    return "\n".join(lines)


class LongitudinalCareAdvisor(RunLoggingMixin, AgentPlugin):
    """Reviews each locked encounter against the patient's history of open recommendations.

    State lives in the plugin's :class:`Recommendation` Custom Data table, not
    in :class:`AgentState`. ``load_state``/``save_state`` are intentionally
    near-empty here: the durable record is the queryable model, and the agent
    reads/writes it via the standard ORM inside ``run()``. This is the "lean
    on existing per-customer primitives" pattern from doc §5.1.
    """

    def load_state(self, scope_key: str) -> AgentState:
        """No serialized state — durable state lives in the Recommendation table."""
        return AgentState()

    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict,
    ) -> AgentRunResult:
        """Verify prior recs, brief the model on context, drive a tool-use loop."""
        patient_id = trigger_payload["patient_id"]
        note_id = trigger_payload["note_id"]

        # Resolve proxies BEFORE asking the model to reason — the agent should
        # see the up-to-date status of every prior recommendation.
        _verify_open_recommendations(patient_id)

        patient = Patient.objects.get(id=patient_id)
        context_block = _format_recommendation_context(patient_id)

        # Shared context threaded into every tool invocation. patient_id and
        # note_id are platform-controlled; effects is the accumulator the
        # propose_recommendation tool appends into.
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
            # Plain assignment — RestrictedPython forbids augmented attribute
            # assignment (`self.x += 1`) in the sandbox.
            self._llm_turn_count = self._llm_turn_count + 1
            response = client.messages.create(
                model=gateway.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=cast(Any, tools.definitions()),
                messages=cast(Any, messages),
            )
            log.info(
                f"LongitudinalCareAdvisor turn={turn} stop_reason={response.stop_reason} "
                f"blocks={[b.type for b in response.content]}"
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                break

            if response.stop_reason == "tool_use":
                tool_results: list[dict] = []
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
        """No-op — durable state was already persisted to Custom Data inside run()."""
        return None
