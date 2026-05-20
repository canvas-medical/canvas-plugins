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

from datetime import date
from typing import Any

from canvas_sdk.agents.tool_registry import ToolRegistry
from canvas_sdk.v1.data import Assessment, Condition, LabValue, Medication, Patient

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


@standard_tools.tool(
    name="find_conditions",
    description=(
        "Search the patient's conditions with optional filters. Returns each "
        "matching condition with `code` (the first coding's identifier — typically "
        "ICD-10), `display`, `clinical_status` (active, resolved, remission, "
        "relapse, investigative), `onset_date` (ISO 8601 or null), and "
        "`resolution_date` (ISO 8601 or null). Defaults to active conditions only, "
        "ordered most-recently-onset first."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "name_contains": {
                "type": "string",
                "description": (
                    "Case-insensitive substring match on the coding display (e.g. 'diabetes')."
                ),
            },
            "code_contains": {
                "type": "string",
                "description": (
                    "Case-insensitive substring match on the coding code "
                    "(e.g. 'E11' for type-2 diabetes ICD-10 family)."
                ),
            },
            "active_only": {
                "type": "boolean",
                "description": (
                    "When true (default), restrict to currently-active conditions. "
                    "When false, include resolved/remission/etc."
                ),
            },
            "onset_on_or_after": {
                "type": "string",
                "format": "date",
                "description": ("ISO 8601 date. Only return conditions with onset_date >= this."),
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Max results. Defaults to 25.",
            },
        },
    },
)
def _find_conditions(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Filter-spec conditions search; patient scope is non-negotiable."""
    patient_id: str = ctx["patient_id"]
    active_only = arguments.get("active_only", True)

    queryset = (
        Condition.objects.active() if active_only else Condition.objects.committed()
    ).filter(patient__id=patient_id)

    if name_contains := arguments.get("name_contains"):
        queryset = queryset.filter(codings__display__icontains=name_contains)

    if code_contains := arguments.get("code_contains"):
        queryset = queryset.filter(codings__code__icontains=code_contains)

    if onset_on_or_after := arguments.get("onset_on_or_after"):
        queryset = queryset.filter(onset_date__gte=onset_on_or_after)

    limit = min(max(int(arguments.get("limit", 25)), 1), 100)
    queryset = queryset.prefetch_related("codings").order_by("-onset_date")[:limit]

    out: list[dict[str, Any]] = []
    for condition in queryset:
        coding = condition.codings.first()
        out.append(
            {
                "code": coding.code if coding else None,
                "display": coding.display if coding else "(unknown)",
                "clinical_status": condition.clinical_status,
                "onset_date": (condition.onset_date.isoformat() if condition.onset_date else None),
                "resolution_date": (
                    condition.resolution_date.isoformat() if condition.resolution_date else None
                ),
            }
        )
    return out


@standard_tools.tool(
    name="find_lab_results",
    description=(
        "Search the patient's committed lab results. Returns each matching value "
        "with `test` (lab name), `value`, `units`, `abnormal_flag` (e.g. 'H', 'L', "
        "or null when normal), and `date` (the report's original_date, ISO 8601). "
        "Defaults to the 10 most-recent results."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "name_contains": {
                "type": "string",
                "description": (
                    "Case-insensitive substring match on the lab's coding name "
                    "(e.g. 'a1c', 'hemoglobin')."
                ),
            },
            "observed_on_or_after": {
                "type": "string",
                "format": "date",
                "description": "ISO 8601 date. Only return results with date >= this.",
            },
            "abnormal_only": {
                "type": "boolean",
                "description": (
                    "When true, restrict to values with a non-empty abnormal_flag. "
                    "Useful for spotting out-of-range results quickly."
                ),
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "description": "Max results. Defaults to 10.",
            },
        },
    },
)
def _find_lab_results(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Filter-spec lab results search; patient scope and junked-filter enforced."""
    patient_id: str = ctx["patient_id"]
    queryset = LabValue.objects.filter(report__patient__id=patient_id, report__junked=False)

    if name_contains := arguments.get("name_contains"):
        queryset = queryset.filter(codings__name__icontains=name_contains)

    if observed_on_or_after := arguments.get("observed_on_or_after"):
        queryset = queryset.filter(report__original_date__gte=observed_on_or_after)

    if arguments.get("abnormal_only"):
        queryset = queryset.exclude(abnormal_flag="").exclude(abnormal_flag__isnull=True)

    limit = min(max(int(arguments.get("limit", 10)), 1), 50)
    queryset = (
        queryset.select_related("report")
        .prefetch_related("codings")
        .order_by("-report__original_date")[:limit]
    )

    out: list[dict[str, Any]] = []
    for value in queryset:
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


@standard_tools.tool(
    name="find_assessments",
    description=(
        "Return the patient's recent clinical assessments (the structured "
        "Assess command's status + narrative on a note). Each result has "
        "`status` ('improved', 'stable', 'deteriorated'), `narrative`, "
        "`background`, `condition_display` (the associated condition's name, "
        "if any), and `date` (the source note's datetime_of_service, ISO 8601). "
        "Ordered most-recent first."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 25,
                "description": "Max results. Defaults to 10.",
            },
        },
    },
)
def _find_assessments(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Recent assessments, ordered by source note's datetime_of_service."""
    patient_id: str = ctx["patient_id"]
    limit = min(max(int(arguments.get("limit", 10)), 1), 25)
    queryset = (
        Assessment.objects.filter(patient__id=patient_id)
        .select_related("note", "condition")
        .prefetch_related("condition__codings")
        .order_by("-note__datetime_of_service")[:limit]
    )

    out: list[dict[str, Any]] = []
    for assessment in queryset:
        condition_display = ""
        condition = assessment.condition
        if condition is not None:
            coding = condition.codings.first()
            if coding:
                condition_display = coding.display
        note_datetime = assessment.note.datetime_of_service if assessment.note else None
        out.append(
            {
                "status": assessment.status,
                "narrative": assessment.narrative,
                "background": assessment.background,
                "condition_display": condition_display,
                "date": note_datetime.isoformat() if note_datetime else None,
            }
        )
    return out


@standard_tools.tool(
    name="get_patient_demographics",
    description=(
        "Return basic demographics for the current patient: legal name, "
        "preferred name, MRN, date of birth, computed age in years, "
        "sex_at_birth, gender_identity, preferred_pronouns, and whether "
        "they're marked deceased. Takes no arguments."
    ),
    input_schema={"type": "object", "properties": {}},
)
def _get_patient_demographics(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Return one patient's identity + demographic basics from the Patient row."""
    patient_id: str = ctx["patient_id"]
    patient = Patient.objects.get(id=patient_id)

    age_years: int | None = None
    if patient.birth_date:
        today = date.today()
        age_years = today.year - patient.birth_date.year
        if (today.month, today.day) < (patient.birth_date.month, patient.birth_date.day):
            age_years -= 1

    return {
        "first_name": patient.first_name,
        "middle_name": patient.middle_name or None,
        "last_name": patient.last_name,
        "preferred_name": patient.nickname or None,
        "mrn": patient.mrn,
        "birth_date": patient.birth_date.isoformat() if patient.birth_date else None,
        "age_years": age_years,
        "sex_at_birth": patient.sex_at_birth or None,
        "gender_identity": patient.gender_identity_term or None,
        "preferred_pronouns": patient.preferred_pronouns or None,
        "deceased": bool(patient.deceased),
    }


__exports__ = ("standard_tools",)
