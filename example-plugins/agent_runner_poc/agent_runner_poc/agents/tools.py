"""Tools exposed to the ChartSummary agent.

The :data:`tools` registry merges two sources:

1. **SDK-provided** :data:`canvas_sdk.agents.standard_tools` — the Canvas-blessed
   tool catalog. Currently ships ``find_medications`` (a filter-spec tool over
   :class:`canvas_sdk.v1.data.Medication`) and will grow over time.
2. **Plugin-defined** read tools (``list_active_conditions``,
   ``recent_lab_results``) and effect tool (``originate_plan``) — registered
   below via the :meth:`ToolRegistry.tool` decorator.

The agent's ``run()`` calls ``tools.definitions()`` to populate the model's
tool list and ``tools.execute(name, args, ctx=...)`` to dispatch tool calls.
"""

from typing import Any

from canvas_sdk.agents import ToolRegistry, standard_tools
from canvas_sdk.commands import PlanCommand
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import Condition, LabValue

tools = ToolRegistry()
tools.extend(standard_tools)


@tools.tool(
    name="list_active_conditions",
    description=(
        "Return the patient's active (committed, non-resolved) conditions "
        "as a list of objects with `code` (the first coding's identifier, "
        "typically ICD-10) and `display`. Use this to understand the "
        "patient's current problem list before drafting a Plan. Returns "
        "up to 50 conditions; if the patient has more, only the first 50 "
        "are returned."
    ),
    input_schema={
        "type": "object",
        "properties": {},
    },
)
def _list_active_conditions(
    arguments: dict[str, Any], *, ctx: dict[str, Any]
) -> list[dict[str, str]]:
    """Active conditions: ICD-10 code + display from the first coding on each."""
    patient_id: str = ctx["patient_id"]
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


@tools.tool(
    name="recent_lab_results",
    description=(
        "Return the patient's most recent committed lab values in "
        "reverse-chronological order, each with `test` (the lab name), "
        "`value`, `units`, `abnormal_flag` (e.g. 'H', 'L', '' if normal), "
        "and `date` (ISO 8601). Use this to spot trends or out-of-range "
        "results worth addressing in the Plan."
    ),
    input_schema={
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
)
def _recent_lab_results(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Most-recent committed lab values, with the report's date and abnormal flag."""
    patient_id: str = ctx["patient_id"]
    limit = min(max(int(arguments.get("limit", 10)), 1), 50)
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


@tools.tool(
    name="originate_plan",
    description=(
        "Stage a Plan command on the patient's current note. Call this "
        "exactly once, when you have enough chart context to draft a "
        "useful Plan. The narrative argument is the plain-text Plan "
        "section (no preamble, no headings, no markdown — <= 3 "
        "sentences). The command is queued as an originated (draft) "
        "command and emitted by the platform when this agent run "
        "completes; this tool does not return the command id."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "narrative": {
                "type": "string",
                "description": "The Plan-section narrative as plain text.",
            },
        },
        "required": ["narrative"],
    },
)
def _originate_plan(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage a Plan command into the agent's effects accumulator.

    The effect is queued, not emitted: ``handle_effect`` won't see it until
    the agent's ``run()`` returns the accumulator in ``AgentRunResult.effects``.
    That single emission point keeps the doc §6.5 idempotency-key story
    coherent and matches the "platform owns when, plugin owns what" split.
    """
    effects: list[Effect] = ctx["effects"]
    note_id: str = ctx["note_id"]
    narrative: str = arguments["narrative"].strip()
    effects.append(PlanCommand(note_uuid=note_id, narrative=narrative).originate())
    return {"ok": True, "queued": True}
