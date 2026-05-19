"""SDK-provided agent tools.

The :data:`standard_tools` registry holds the Canvas-blessed tool catalog —
opinionated wrappers around clinical data reads, with the patient-scope
filter applied implicitly so the model can't accidentally cross into another
patient's chart. Plugin authors layer their own tools on top via
:meth:`ToolRegistry.extend`.

Filter-spec design (per the discussion in canvas-medical/canvas-plugins#1713):
each tool exposes a small set of structured filter parameters the model can
combine, rather than pre-baking many narrow tool variants. The tool author
controls *which* fields are filterable and *which* lookups are allowed —
enough flexibility to cover most cases, while keeping clinical semantics
and tenant-scope enforced.
"""

from typing import Any

from canvas_sdk.agents.tool_registry import ToolRegistry
from canvas_sdk.v1.data import Medication

standard_tools = ToolRegistry()


@standard_tools.tool(
    name="find_medications",
    description=(
        "Search the patient's medications with optional filters. Returns each "
        "matching medication as an object with `name` (display from the first "
        'coding, typically RxNorm), `status` ("active" or "inactive"), '
        "`start_date` (ISO 8601 or null), and `end_date` (ISO 8601 or null). "
        "Patient scope is enforced — the tool only returns records for the "
        "current agent's patient. If no filters are supplied, returns the most "
        "recent records by start_date."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "name_contains": {
                "type": "string",
                "description": (
                    "Case-insensitive substring match against the medication's "
                    "first-coding display. E.g. 'metformin' matches "
                    "'Metformin 500 mg tablet'."
                ),
            },
            "active_only": {
                "type": "boolean",
                "description": (
                    "When true, restrict to active (status='active', committed) "
                    "medications. When false or omitted, include inactive too."
                ),
            },
            "started_on_or_after": {
                "type": "string",
                "format": "date",
                "description": (
                    "ISO 8601 date (YYYY-MM-DD). When supplied, only return "
                    "medications with start_date >= this value."
                ),
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Maximum results to return. Defaults to 25.",
            },
        },
    },
)
def _find_medications(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Filter-spec medications search; patient scope is non-negotiable."""
    patient_id: str = ctx["patient_id"]

    queryset = (
        Medication.objects.active()
        if arguments.get("active_only")
        else Medication.objects.committed()
    )
    queryset = queryset.filter(patient__id=patient_id)

    if name_contains := arguments.get("name_contains"):
        queryset = queryset.filter(codings__display__icontains=name_contains)

    if started_on_or_after := arguments.get("started_on_or_after"):
        queryset = queryset.filter(start_date__gte=started_on_or_after)

    limit = min(max(int(arguments.get("limit", 25)), 1), 100)
    queryset = queryset.prefetch_related("codings").order_by("-start_date")[:limit]

    out: list[dict[str, Any]] = []
    for medication in queryset:
        coding = medication.codings.first()
        name = coding.display if coding else "(unknown)"
        out.append(
            {
                "name": name,
                "status": medication.status,
                "start_date": (
                    medication.start_date.isoformat() if medication.start_date else None
                ),
                "end_date": medication.end_date.isoformat() if medication.end_date else None,
            }
        )
    return out


__exports__ = ("standard_tools",)
