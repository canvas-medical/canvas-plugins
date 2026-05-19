import json
from typing import Any, cast

from anthropic import Anthropic
from anthropic.types import ToolUseBlock

from agent_runner_poc.agents.tools import TOOLS, execute_tool
from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, LLMGateway
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import Patient
from logger import log

SYSTEM_PROMPT = (
    "You are a clinical documentation assistant drafting a follow-up Plan-section "
    "narrative for a newly-created encounter note. You have read tools to inspect "
    "the patient's active conditions and recent lab results, and one effect tool "
    "(`originate_plan`) that stages the Plan command. Workflow: read the chart "
    "with the read tools, draft a concise Plan grounded in what you found, then "
    "call `originate_plan` exactly once with the narrative as plain text "
    "(<= 3 sentences, no preamble, no headings, no markdown). After the tool "
    "returns, you may end your turn — no further text is required."
)

MAX_TURNS = 8


class ChartSummary(AgentPlugin):
    """Drafts a Plan command for a new note via tool-driven chart reads.

    The model owns the action: it calls ``originate_plan`` to stage the Plan
    command into the agent's effects accumulator. The framework dispatches
    every effect in the accumulator through ``handle_effect`` exactly once
    after ``run()`` returns and ``save_state`` commits.

    PoC scope: no persisted state.
    """

    def load_state(self, scope_key: str) -> AgentState:
        """Single-shot agent — no prior state to load."""
        return AgentState()

    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict,
    ) -> AgentRunResult:
        """Drive a multi-turn tool-use loop; emit whatever effects the model staged."""
        note_id = trigger_payload["note_id"]
        patient_id = trigger_payload["patient_id"]
        patient = Patient.objects.get(id=patient_id)

        # Shared context threaded into every tool invocation. The model only
        # ever sees `arguments` (its own tool_use input); patient_id, note_id,
        # and the effects accumulator are platform-controlled.
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
                    f"Draft a follow-up Plan for patient {patient.first_name} "
                    f"{patient.last_name}. Inspect the chart with the read "
                    "tools, then call `originate_plan` once with your draft."
                ),
            }
        ]

        for turn in range(MAX_TURNS):
            response = client.messages.create(
                model=gateway.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                # Anthropic SDK stubs expect typed param TypedDicts here; the
                # runtime accepts our plain-dict shapes equivalently.
                tools=cast(Any, TOOLS),
                messages=cast(Any, messages),
            )
            log.info(
                f"ChartSummary turn={turn} stop_reason={response.stop_reason} "
                f"blocks={[b.type for b in response.content]}"
            )

            # Persist the assistant turn into history before deciding what to do next.
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                break

            if response.stop_reason == "tool_use":
                tool_results: list[dict] = []
                for block in response.content:
                    if not isinstance(block, ToolUseBlock):
                        continue
                    try:
                        result = execute_tool(block.name, dict(block.input), ctx=tool_ctx)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result, default=str),
                            }
                        )
                    except Exception as exc:
                        log.exception(f"ChartSummary: tool {block.name!r} raised")
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

            log.warning(f"ChartSummary: unexpected stop_reason={response.stop_reason!r}; bailing")
            break
        else:
            log.warning(
                f"ChartSummary: hit MAX_TURNS={MAX_TURNS} without end_turn; "
                "returning whatever was staged"
            )

        log.info(f"ChartSummary loop complete for note {note_id}; {len(effects)} effect(s) staged")
        return AgentRunResult(state=state, effects=effects)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """Single-shot agent — nothing to persist."""
        return None
