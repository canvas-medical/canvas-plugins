"""Tools exposed to the ChartSummary agent's Anthropic LLM call.

This is the plugin author's tool catalog — a list of JSON-Schema definitions
in :data:`TOOLS` plus an :func:`execute_tool` dispatcher that bridges to
Canvas SDK reads.

The agent's ``run()`` method threads ``patient_id`` (and any other contextual
identifiers from the trigger payload) through ``execute_tool`` directly.
Tool inputs from the model only carry parameters the model is *choosing*
(like ``limit``); the model never decides which patient a tool reads — that
identity is bound by the trigger that fired the agent.

For the PoC we expose two read tools. Effect-emitting tools (e.g.
``propose_action_for_review``) are deferred — the agent emits its Plan
command through the normal ``AgentRunResult.effects`` return after the
LLM loop terminates, not from inside a tool.
"""

from typing import Any

from canvas_sdk.commands import PlanCommand
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import Condition, LabValue

TOOLS: list[dict[str, Any]] = [
    {
        "name": "list_active_conditions",
        "description": (
            "Return the patient's active (committed, non-resolved) conditions "
            "as a list of objects with `code` (the first coding's identifier, "
            "typically ICD-10) and `display`. Use this to understand the "
            "patient's current problem list before drafting a Plan. Returns "
            "up to 50 conditions; if the patient has more, only the first 50 "
            "are returned."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "recent_lab_results",
        "description": (
            "Return the patient's most recent committed lab values in "
            "reverse-chronological order, each with `test` (the lab name), "
            "`value`, `units`, `abnormal_flag` (e.g. 'H', 'L', '' if normal), "
            "and `date` (ISO 8601). Use this to spot trends or out-of-range "
            "results worth addressing in the Plan."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": (
                        "Maximum number of lab values to return. Defaults to "
                        "10. The implementation caps the request at 50."
                    ),
                    "minimum": 1,
                    "maximum": 50,
                },
            },
        },
    },
    {
        "name": "originate_plan",
        "description": (
            "Stage a Plan command on the patient's current note. Call this "
            "exactly once, when you have enough chart context to draft a "
            "useful Plan. The narrative argument is the plain-text Plan "
            "section (no preamble, no headings, no markdown — <= 3 "
            "sentences). The command is queued as an originated (draft) "
            "command and emitted by the platform when this agent run "
            "completes; this tool does not return the command id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "narrative": {
                    "type": "string",
                    "description": "The Plan-section narrative as plain text.",
                },
            },
            "required": ["narrative"],
        },
    },
]


def execute_tool(name: str, arguments: dict, *, ctx: dict[str, Any]) -> Any:
    """Dispatch a model-issued tool call to its Canvas-side implementation.

    Args:
        name: The tool name as declared in :data:`TOOLS`.
        arguments: The tool's inputs as parsed from the model's tool_use block.
        ctx: Caller-supplied context. Required keys:

            - ``patient_id`` (str): UUID of the patient the agent is reasoning
              about; threaded into every read tool so the model never gets to
              choose which patient a read targets.
            - ``note_id`` (str): UUID of the note the agent should originate
              effects against. Threaded into effect-emitting tools.
            - ``effects`` (list[Effect]): Mutable accumulator. Effect-emitting
              tools append into this list; the agent's ``run()`` returns the
              accumulator in ``AgentRunResult.effects``, where the framework
              dispatches each effect through ``handle_effect`` exactly once
              after ``save_state`` commits.

    Returns:
        A JSON-serializable value the caller will send back to the model as
        the ``tool_result`` content. Effect-emitting tools return a small
        acknowledgement ({"ok": True, "queued": True}); the actual emission
        happens platform-side after ``run()`` returns.

    Raises:
        ValueError: If ``name`` is not a known tool. The caller should
            translate this into a ``tool_result`` with ``is_error=True``
            instead of crashing the run.
    """
    patient_id: str = ctx["patient_id"]
    if name == "list_active_conditions":
        return _list_active_conditions(patient_id)
    if name == "recent_lab_results":
        limit = min(max(int(arguments.get("limit", 10)), 1), 50)
        return _recent_lab_results(patient_id, limit)
    if name == "originate_plan":
        return _originate_plan(
            arguments["narrative"], note_id=ctx["note_id"], effects=ctx["effects"]
        )
    raise ValueError(f"Unknown tool: {name!r}")


def _list_active_conditions(patient_id: str) -> list[dict[str, str]]:
    """Active conditions: ICD-10 code + display from the first coding on each."""
    # `patient_id=...` would match against Patient.dbid (the integer PK the FK
    # column references); traversing the relation as `patient__id=...` matches
    # against Patient.id (the UUID we receive in the trigger payload).
    conditions = (
        Condition.objects.active().filter(patient__id=patient_id).prefetch_related("codings")[:50]
    )
    out: list[dict[str, str]] = []
    for condition in conditions:
        coding = condition.codings.first()
        if coding is None:
            continue
        out.append({"code": coding.code, "display": coding.display})
    return out


def _recent_lab_results(patient_id: str, limit: int) -> list[dict[str, Any]]:
    """Most-recent committed lab values, with the report's date and abnormal flag."""
    values = (
        LabValue.objects.filter(report__patient__id=patient_id, report__junked=False)
        .select_related("report")
        .prefetch_related("codings")
        .order_by("-report__original_date")[:limit]
    )
    out: list[dict[str, Any]] = []
    for value in values:
        coding = value.codings.first()
        test_name = coding.name if coding else "(unknown)"
        report_date = value.report.original_date if value.report else None
        out.append(
            {
                "test": test_name,
                "value": value.value,
                "units": value.units,
                "abnormal_flag": value.abnormal_flag or None,
                "date": report_date.isoformat() if report_date else None,
            }
        )
    return out


def _originate_plan(narrative: str, *, note_id: str, effects: list[Effect]) -> dict[str, Any]:
    """Stage a Plan command into the agent's effects accumulator.

    The effect is queued, not emitted: ``handle_effect`` won't see it until
    the agent's ``run()`` returns the accumulator in ``AgentRunResult.effects``.
    That single emission point keeps the doc §6.5 idempotency-key story
    coherent and matches the "platform owns when, plugin owns what" split.
    """
    effects.append(PlanCommand(note_uuid=note_id, narrative=narrative.strip()).originate())
    return {"ok": True, "queued": True}
