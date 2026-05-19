"""Tools exposed to the ChartChatAgent.

Read-only catalog for the chat surface. The chat agent doesn't emit effects
— it returns plain-text responses that the SimpleAPI handler relays back to
the UI. (Future enhancement: add effect tools like ``propose_task`` so the
agent can offer actionable suggestions inline. For phase 1, just text.)
"""

from typing import Any

from canvas_sdk.agents import ToolRegistry, standard_tools
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
    input_schema={"type": "object", "properties": {}},
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
        "reverse-chronological order, each with `test`, `value`, `units`, "
        "`abnormal_flag`, and `date`."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "description": "Max values to return; defaults to 10, capped at 50.",
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
