"""Tools exposed to the LongitudinalCareAdvisor agent.

Same compose-from-standard-tools pattern as ``tools.py`` (the ChartSummary
tools): start with the SDK catalog via ``extend(standard_tools)``, then
register plugin-specific tools on top. The advisor's effect tool is
``propose_recommendation``, which both writes a :class:`Recommendation` row
to the plugin's Custom Data (so the agent has memory across encounters) and
stages a :class:`AddTask` effect (so the clinician sees the follow-up).

The Task's UUID is generated client-side and stored in both the
Recommendation's ``proxy_data["task_id"]`` and the AddTask effect's ``id``,
so the next run's verifier can do an exact ``Task.objects.get(id=...)``
lookup instead of loose narrative matching.
"""

from typing import Any
from uuid import uuid4

from agent_runner_poc.models.proxy import PatientProxy
from agent_runner_poc.models.recommendation import Recommendation
from canvas_sdk.agents import ToolRegistry, standard_tools
from canvas_sdk.effects import Effect
from canvas_sdk.effects.task.task import AddTask
from canvas_sdk.v1.data import Condition, LabValue

tools = ToolRegistry()
tools.extend(standard_tools)


@tools.tool(
    name="list_active_conditions",
    description=(
        "Return the patient's active (committed, non-resolved) conditions "
        "as a list of objects with `code` (the first coding's identifier, "
        "typically ICD-10) and `display`. Returns up to 50."
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
        "reverse-chronological order, each with `test` (lab name), `value`, "
        "`units`, `abnormal_flag`, and `date` (ISO 8601). Use this to spot "
        "trends or out-of-range results."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of lab values to return. Defaults to 10. Capped at 50.",
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
    name="propose_recommendation",
    description=(
        "Propose a follow-up recommendation and surface it to the clinician "
        "as a Task. The recommendation is also persisted to the plugin's "
        "Custom Data so the agent can check on subsequent runs whether the "
        "clinician acted on it. Call this once per distinct recommendation; "
        "do NOT re-propose recommendations the agent already shows as open "
        "(those resurface automatically).\n\n"
        "Categories drive how the next run verifies whether the "
        "recommendation was addressed:\n"
        "- `task`: verified by the emitted Task being marked complete. "
        "Use for anything where the clinician acting is the success signal "
        "(e.g. 'discuss medication adherence at next visit').\n"
        "- `follow_up_lab`: verified by a matching lab result arriving. "
        "Supply `proxy_data.loinc` with the lab's LOINC code (e.g. '4548-4' "
        "for hemoglobin A1c). Use for 'recheck X in N months'.\n"
        "- `none`: no automatic verification. The task resurfaces every "
        "visit until the clinician completes it. Use sparingly."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "narrative": {
                "type": "string",
                "description": (
                    "Plain-text recommendation, <= 200 chars (used as the "
                    "Task title). No preamble, no markdown."
                ),
            },
            "category": {
                "type": "string",
                "enum": ["task", "follow_up_lab", "none"],
                "description": "How the next run should verify this recommendation.",
            },
            "proxy_data": {
                "type": "object",
                "description": (
                    "Category-specific verifier hints. For `follow_up_lab`, "
                    "include `loinc`. For `task` or `none`, omit or pass {}."
                ),
            },
        },
        "required": ["narrative", "category"],
    },
)
def _propose_recommendation(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Persist a Recommendation row and stage an AddTask effect to surface it."""
    patient_id: str = ctx["patient_id"]
    effects: list[Effect] = ctx["effects"]

    narrative: str = arguments["narrative"].strip()
    category: str = arguments["category"]
    proxy_data: dict[str, Any] = dict(arguments.get("proxy_data") or {})

    # Client-generate the Task UUID so the Recommendation row can hold a hard
    # reference to it. The AddTask effect ingest path on home-app honors the
    # supplied id rather than assigning its own.
    task_id = str(uuid4())
    proxy_data["task_id"] = task_id

    patient = PatientProxy.objects.get(id=patient_id)
    recommendation = Recommendation.objects.create(
        patient=patient,
        narrative=narrative,
        category=category,
        proxy_data=proxy_data,
    )

    effects.append(
        AddTask(
            id=task_id,
            patient_id=patient_id,
            title=narrative[:200],
        ).apply()
    )

    return {
        "ok": True,
        "recommendation_id": str(recommendation.id),
        "task_id": task_id,
        "queued_task": True,
    }
