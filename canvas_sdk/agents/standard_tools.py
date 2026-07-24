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

Most tools use :meth:`ToolRegistry.filter_search_tool` — a helper that takes
a queryset factory, a filter spec, and a per-row serializer and synthesizes
the JSON Schema, executor, and registration. Anything that doesn't fit the
filter-search shape (e.g., scalar reads like ``get_patient_demographics``)
is hand-registered via :meth:`ToolRegistry.tool`.
"""

import re
from datetime import UTC, date, datetime
from typing import Any
from uuid import uuid4

from django.db.models import Q

from canvas_sdk.agents.note_helpers import find_open_note
from canvas_sdk.agents.tool_registry import EffectField, FilterSpec, ToolRegistry
from canvas_sdk.commands import (
    AssessCommand,
    DiagnoseCommand,
    FollowUpCommand,
    GoalCommand,
    ImagingOrderCommand,
    InstructCommand,
    LabOrderCommand,
    PlanCommand,
    PrescribeCommand,
    ReferCommand,
    StopMedicationCommand,
)
from canvas_sdk.effects.banner_alert.add_banner_alert import AddBannerAlert
from canvas_sdk.effects.banner_alert.remove_banner_alert import RemoveBannerAlert
from canvas_sdk.effects.note.message import Message as MessageEffect
from canvas_sdk.effects.note.note import Note as NoteEffect
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard, Recommendation
from canvas_sdk.effects.task.task import AddTask, AddTaskComment, TaskStatus, UpdateTask
from canvas_sdk.v1.data import (
    AllergyIntolerance,
    Appointment,
    Assessment,
    BannerAlert,
    CareTeamMembership,
    Command,
    Condition,
    Encounter,
    ExternalEvent,
    Goal,
    ImagingReport,
    Immunization,
    Interview,
    LabPartner,
    LabPartnerTest,
    LabValue,
    Medication,
    MedicationStatement,
    Message,
    Note,
    NoteType,
    Observation,
    Patient,
    PracticeLocation,
    Prescription,
    ProtocolCurrent,
    Referral,
    StopMedicationEvent,
    Task,
)
from canvas_sdk.v1.data.appointment import AppointmentProgressStatus
from canvas_sdk.v1.data.care_team import CareTeamMembershipStatus
from canvas_sdk.v1.data.encounter import EncounterState
from canvas_sdk.v1.data.goal import GoalAchievementStatus, GoalLifecycleStatus, GoalPriority
from canvas_sdk.v1.data.note import NoteStates, NoteTypeCategories

standard_tools = ToolRegistry()


@standard_tools.filter_search_tool(
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
    queryset_factory=lambda args, pid: (
        Medication.objects.active() if args.get("active_only") else Medication.objects.committed()
    ).filter(patient__id=pid),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match against the medication's "
                "first-coding display. E.g. 'metformin' matches "
                "'Metformin 500 mg tablet'."
            ),
            apply=lambda qs, v: qs.filter(codings__display__icontains=v),
        ),
        "active_only": FilterSpec(
            type="boolean",
            description=(
                "When true, restrict to active (status='active', committed) "
                "medications. When false or omitted, include inactive too."
            ),
            # No apply — queryset_factory consumes this.
        ),
        "started_on_or_after": FilterSpec(
            type="string",
            format="date",
            description=(
                "ISO 8601 date (YYYY-MM-DD). When supplied, only return "
                "medications with start_date >= this value."
            ),
            apply=lambda qs, v: qs.filter(start_date__gte=v),
        ),
    },
    ordering=("-start_date",),
    prefetch_related=("codings",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=Medication,
    returns_description=(
        "Array of objects with `id`, `name`, `status` (active|inactive), "
        "`start_date` (ISO 8601 or null), `end_date` (ISO 8601 or null)."
    ),
)
def _serialize_medication(medication: Any) -> dict[str, Any]:
    """Per-row serializer for find_medications."""
    coding = medication.codings.first()
    return {
        "id": str(medication.id),
        "name": coding.display if coding else "(unknown)",
        "status": medication.status,
        "start_date": medication.start_date.isoformat() if medication.start_date else None,
        "end_date": medication.end_date.isoformat() if medication.end_date else None,
    }


@standard_tools.filter_search_tool(
    name="find_conditions",
    description=(
        "Search the patient's conditions with optional filters. Returns each "
        "matching condition with `code` (the first coding's identifier — typically "
        "ICD-10), `display`, `clinical_status` (active, resolved, remission, "
        "relapse, investigative), `onset_date` (ISO 8601 or null), and "
        "`resolution_date` (ISO 8601 or null). Defaults to active conditions only, "
        "ordered most-recently-onset first."
    ),
    queryset_factory=lambda args, pid: (
        Condition.objects.active()
        if args.get("active_only", True)
        else Condition.objects.committed()
    ).filter(patient__id=pid),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the coding display (e.g. 'diabetes')."
            ),
            apply=lambda qs, v: qs.filter(codings__display__icontains=v),
        ),
        "code_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the coding code "
                "(e.g. 'E11' for type-2 diabetes ICD-10 family)."
            ),
            apply=lambda qs, v: qs.filter(codings__code__icontains=v),
        ),
        "active_only": FilterSpec(
            type="boolean",
            description=(
                "When true (default), restrict to currently-active conditions. "
                "When false, include resolved/remission/etc."
            ),
            # No apply — queryset_factory consumes this.
        ),
        "onset_on_or_after": FilterSpec(
            type="string",
            format="date",
            description="ISO 8601 date. Only return conditions with onset_date >= this.",
            apply=lambda qs, v: qs.filter(onset_date__gte=v),
        ),
    },
    ordering=("-onset_date",),
    prefetch_related=("codings",),
    limit_default=25,
    limit_max=100,
    limit_description="Max results. Defaults to 25.",
    categories=("clinical_reads",),
    model=Condition,
    returns_description=(
        "Array of objects with `id`, `code`, `display`, `clinical_status` "
        "(active|resolved|remission|relapse|investigative), `onset_date`, "
        "`resolution_date`."
    ),
)
def _serialize_condition(condition: Any) -> dict[str, Any]:
    """Per-row serializer for find_conditions."""
    coding = condition.codings.first()
    return {
        "id": str(condition.id),
        "code": coding.code if coding else None,
        "display": coding.display if coding else "(unknown)",
        "clinical_status": condition.clinical_status,
        "onset_date": condition.onset_date.isoformat() if condition.onset_date else None,
        "resolution_date": (
            condition.resolution_date.isoformat() if condition.resolution_date else None
        ),
    }


@standard_tools.filter_search_tool(
    name="find_lab_results",
    description=(
        "Search the patient's committed lab results. Returns each matching value "
        "with `test` (lab name), `value`, `units`, `abnormal_flag` (e.g. 'H', 'L', "
        "or null when normal), and `date` (the report's original_date, ISO 8601). "
        "Defaults to the 10 most-recent results."
    ),
    queryset_factory=lambda args, pid: LabValue.objects.filter(
        report__patient__id=pid, report__junked=False
    ),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the lab's coding name "
                "(e.g. 'a1c', 'hemoglobin')."
            ),
            apply=lambda qs, v: qs.filter(codings__name__icontains=v),
        ),
        "observed_on_or_after": FilterSpec(
            type="string",
            format="date",
            description="ISO 8601 date. Only return results with date >= this.",
            apply=lambda qs, v: qs.filter(report__original_date__gte=v),
        ),
        "abnormal_only": FilterSpec(
            type="boolean",
            description=(
                "When true, restrict to values with a non-empty abnormal_flag. "
                "Useful for spotting out-of-range results quickly."
            ),
            apply=lambda qs, _v: qs.exclude(abnormal_flag="").exclude(abnormal_flag__isnull=True),
        ),
    },
    ordering=("-report__original_date",),
    select_related=("report",),
    prefetch_related=("codings",),
    limit_default=10,
    limit_max=50,
    limit_description="Max results. Defaults to 10.",
    categories=("clinical_reads",),
    model=LabValue,
    returns_description=(
        "Array of objects with `id`, `test`, `value`, `units`, "
        "`abnormal_flag` (e.g. 'H', 'L', or null), `date`."
    ),
)
def _serialize_lab_value(value: Any) -> dict[str, Any]:
    """Per-row serializer for find_lab_results."""
    coding = value.codings.first()
    report_date = value.report.original_date if value.report else None
    return {
        "id": str(value.id),
        "test": coding.name if coding else "(unknown)",
        "value": value.value,
        "units": value.units,
        "abnormal_flag": value.abnormal_flag or None,
        "date": report_date.isoformat() if report_date else None,
    }


@standard_tools.filter_search_tool(
    name="find_assessments",
    description=(
        "Return the patient's recent clinical assessments (the structured "
        "Assess command's status + narrative on a note). Each result has "
        "`status` ('improved', 'stable', 'deteriorated'), `narrative`, "
        "`background`, `condition_display` (the associated condition's name, "
        "if any), and `date` (the source note's datetime_of_service, ISO 8601). "
        "Ordered most-recent first."
    ),
    queryset_factory=lambda _args, pid: Assessment.objects.filter(patient__id=pid),
    filters={},
    ordering=("-note__datetime_of_service",),
    select_related=("note", "condition"),
    prefetch_related=("condition__codings",),
    limit_default=10,
    limit_max=25,
    limit_description="Max results. Defaults to 10.",
    categories=("clinical_reads",),
    model=Assessment,
    returns_description=(
        "Array of objects with `id`, `status`, `narrative`, `background`, "
        "`condition_display`, `date`."
    ),
)
def _serialize_assessment(assessment: Any) -> dict[str, Any]:
    """Per-row serializer for find_assessments."""
    condition_display = ""
    condition = assessment.condition
    if condition is not None:
        coding = condition.codings.first()
        if coding:
            condition_display = coding.display
    note_datetime = assessment.note.datetime_of_service if assessment.note else None
    return {
        "id": str(assessment.id),
        "status": assessment.status,
        "narrative": assessment.narrative,
        "background": assessment.background,
        "condition_display": condition_display,
        "date": note_datetime.isoformat() if note_datetime else None,
    }


@standard_tools.filter_search_tool(
    name="find_allergies",
    description=(
        "Search the patient's documented allergies and intolerances. Returns "
        "each entry with `display` (allergen name from the first coding), "
        "`code` (typically RxNorm or SNOMED), `severity` (e.g., 'mild', "
        "'moderate', 'severe'), `narrative` (free-text reaction description), "
        "`status`, and `onset_date` (ISO 8601 or null). Patient scope is "
        "enforced. Defaults to non-deleted committed entries, ordered "
        "most-recently-onset first."
    ),
    queryset_factory=lambda args, pid: AllergyIntolerance.objects.committed().filter(
        patient__id=pid, deleted=False
    ),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the allergen's display "
                "(e.g., 'penicillin', 'peanut', 'sulfa')."
            ),
            apply=lambda qs, v: qs.filter(codings__display__icontains=v),
        ),
        "severity": FilterSpec(
            type="string",
            description=(
                "Filter to a specific severity. Common values: 'mild', "
                "'moderate', 'severe'. Match is case-insensitive exact."
            ),
            apply=lambda qs, v: qs.filter(severity__iexact=v),
        ),
    },
    ordering=("-onset_date",),
    prefetch_related=("codings",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=AllergyIntolerance,
    returns_description=(
        "Array of objects with `id`, `display`, `code`, `severity`, "
        "`narrative`, `status`, `onset_date`."
    ),
)
def _serialize_allergy(allergy: Any) -> dict[str, Any]:
    """Per-row serializer for find_allergies."""
    coding = allergy.codings.first()
    return {
        "id": str(allergy.id),
        "display": coding.display if coding else "(unknown)",
        "code": coding.code if coding else None,
        "severity": allergy.severity or None,
        "narrative": allergy.narrative or None,
        "status": allergy.status or None,
        "onset_date": allergy.onset_date.isoformat() if allergy.onset_date else None,
    }


@standard_tools.filter_search_tool(
    name="find_immunizations",
    description=(
        "Search the patient's immunization history. Returns each entry with "
        "`display` (vaccine name from the first coding, typically CVX), "
        "`code`, `date_administered` (ISO 8601 or null), `status` "
        "(e.g., 'administered', 'refused'), `manufacturer`, and `lot_number`. "
        "Patient scope is enforced. Ordered most-recent first."
    ),
    # Immunization's QuerySet inherits CommittableQuerySetMixin but the model
    # itself has no `committer` field — calling `.committed()` raises. Filter
    # on `deleted=False` directly instead.
    queryset_factory=lambda args, pid: Immunization.objects.filter(patient__id=pid, deleted=False),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the vaccine's display "
                "(e.g., 'influenza', 'covid', 'tdap', 'mmr')."
            ),
            apply=lambda qs, v: qs.filter(codings__display__icontains=v),
        ),
        "given_on_or_after": FilterSpec(
            type="string",
            format="date",
            description=(
                "ISO 8601 date. Only return immunizations with date_ordered >= this value."
            ),
            apply=lambda qs, v: qs.filter(date_ordered__gte=v),
        ),
    },
    ordering=("-date_ordered",),
    prefetch_related=("codings",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=Immunization,
    returns_description=("Array of objects with `id`, `display`, `code`, `given_on`, `status`."),
)
def _serialize_immunization(immunization: Any) -> dict[str, Any]:
    """Per-row serializer for find_immunizations."""
    coding = immunization.codings.first()
    return {
        "id": str(immunization.id),
        "display": coding.display if coding else "(unknown)",
        "code": coding.code if coding else None,
        "date_administered": (
            immunization.date_ordered.isoformat() if immunization.date_ordered else None
        ),
        "status": immunization.status or None,
        "manufacturer": immunization.manufacturer or None,
        "lot_number": immunization.lot_number or None,
    }


@standard_tools.filter_search_tool(
    name="find_vitals",
    description=(
        "Search the patient's recorded vital signs — blood pressure, heart "
        "rate, temperature, weight, height, BMI, respiratory rate, oxygen "
        "saturation, and similar measurements (any Observation in the "
        "FHIR `vital-signs` category). Returns each measurement with `name`, "
        "`value`, `units`, `code` (typically LOINC from the first coding), "
        "and `date` (ISO 8601 effective_datetime). Patient scope is "
        "enforced. Defaults to the 10 most recent."
    ),
    queryset_factory=lambda args, pid: Observation.objects.committed().filter(
        patient__id=pid, category="vital-signs"
    ),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the observation's name "
                "(e.g., 'blood pressure', 'weight', 'temperature', 'pulse')."
            ),
            apply=lambda qs, v: qs.filter(name__icontains=v),
        ),
        "observed_on_or_after": FilterSpec(
            type="string",
            format="date",
            description=(
                "ISO 8601 date. Only return measurements with effective_datetime >= this value."
            ),
            apply=lambda qs, v: qs.filter(effective_datetime__gte=v),
        ),
    },
    ordering=("-effective_datetime",),
    prefetch_related=("codings",),
    limit_default=10,
    limit_max=50,
    limit_description="Maximum results to return. Defaults to 10.",
    categories=("clinical_reads",),
    model=Observation,
    returns_description=("Array of objects with `id`, `name`, `value`, `units`, `observed_at`."),
)
def _serialize_vital(observation: Any) -> dict[str, Any]:
    """Per-row serializer for find_vitals."""
    coding = observation.codings.first()
    return {
        "id": str(observation.id),
        "name": observation.name or "(unknown)",
        "value": observation.value or None,
        "units": observation.units or None,
        "code": coding.code if coding else None,
        "date": (
            observation.effective_datetime.isoformat() if observation.effective_datetime else None
        ),
    }


def _tasks_queryset(args: dict[str, Any], pid: str) -> Any:
    """Tasks scoped to patient; status defaults to OPEN when not supplied.

    The `status` filter is consumed here entirely (no separate apply) so the
    default-OPEN behavior doesn't conflict with an explicit override.
    """
    queryset = Task.objects.filter(patient__id=pid)
    status_filter = args.get("status")
    if status_filter:
        queryset = queryset.filter(status__iexact=status_filter)
    else:
        queryset = queryset.filter(status="OPEN")
    return queryset


@standard_tools.filter_search_tool(
    name="find_tasks",
    description=(
        "Search tasks linked to the current patient (clinician follow-ups, "
        "outreach reminders, etc.). Returns each task with `id`, `title`, "
        "`status` ('OPEN', 'COMPLETED', 'CLOSED'), `due` (ISO 8601 or null), "
        "and `task_type`. Defaults to OPEN tasks ordered by due date."
    ),
    queryset_factory=_tasks_queryset,
    filters={
        "status": FilterSpec(
            type="string",
            description=("Filter to a specific status. If omitted, defaults to OPEN tasks only."),
            enum=[s.value for s in TaskStatus],
            # No apply — queryset_factory consumes (so the default-OPEN
            # behavior doesn't conflict with an explicit override).
        ),
        "title_contains": FilterSpec(
            type="string",
            description="Case-insensitive substring match on the task title.",
            apply=lambda qs, v: qs.filter(title__icontains=v),
        ),
        "due_on_or_after": FilterSpec(
            type="string",
            format="date",
            description="ISO 8601 date. Only return tasks with due >= this value.",
            apply=lambda qs, v: qs.filter(due__date__gte=v),
        ),
    },
    ordering=("due",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("task_reads",),
    model=Task,
    returns_description=(
        "Array of objects with `id`, `title`, `status`, `due` (ISO 8601), "
        "`assignee_name`, `team_name`, `labels`, `created`."
    ),
)
def _serialize_task(task: Any) -> dict[str, Any]:
    """Per-row serializer for find_tasks."""
    return {
        "id": str(task.id),
        "title": task.title or None,
        "status": task.status or None,
        "due": task.due.isoformat() if task.due else None,
        "task_type": task.task_type or None,
    }


def _person_name(canvas_user: Any) -> str | None:
    """Resolve a CanvasUser to a Patient/Staff display name, or None.

    Used by find_messages to surface sender/recipient names without the
    LLM having to call additional lookup tools. ``person_subclass`` is a
    cached_property that returns the related Patient or Staff row based
    on the user's ``is_staff`` flag.
    """
    if canvas_user is None:
        return None
    try:
        subclass = canvas_user.person_subclass
    except Exception:
        return None
    return getattr(subclass, "full_name", None) or None


def _person_role(canvas_user: Any) -> str | None:
    """Return 'staff' or 'patient' for a CanvasUser, or None if unknown."""
    if canvas_user is None:
        return None
    return "staff" if canvas_user.is_staff else "patient"


@standard_tools.filter_search_tool(
    name="find_messages",
    description=(
        "Search the patient's messages (clinician ↔ patient correspondence "
        "via the patient portal). Returns each message with `id`, `content`, "
        "`sender_role` ('patient' or 'staff'), `sender_name`, "
        "`recipient_role`, `recipient_name`, `sent_at` (ISO 8601), and "
        "`read_at` (ISO 8601 or null). Defaults to the 20 most recent. "
        "Use `from_patient_only=true` to see only incoming messages from "
        "the patient (e.g., to draft a reply); `unread_only=true` to scope "
        "to messages the recipient hasn't read yet; `since=YYYY-MM-DD` to "
        "look at a recent window."
    ),
    queryset_factory=lambda args, pid: Message.objects.filter(note__patient__id=pid).select_related(
        "sender", "recipient"
    ),
    filters={
        "from_patient_only": FilterSpec(
            type="boolean",
            description=(
                "When true, restrict to messages where the sender is a "
                "patient (i.e., incoming messages from this patient to "
                "their care team). Useful for finding the latest message "
                "to reply to."
            ),
            apply=lambda qs, v: qs.filter(sender__is_staff=False) if v else qs,
        ),
        "unread_only": FilterSpec(
            type="boolean",
            description=(
                "When true, restrict to messages with no `read` timestamp "
                "yet — i.e., the recipient hasn't opened them."
            ),
            apply=lambda qs, v: qs.filter(read__isnull=True) if v else qs,
        ),
        "since": FilterSpec(
            type="string",
            format="date",
            description=("ISO 8601 date. Only return messages with created >= this value."),
            apply=lambda qs, v: qs.filter(created__gte=v),
        ),
    },
    ordering=("-created",),
    limit_default=20,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 20.",
    categories=("message_reads",),
    model=Message,
    returns_description=(
        "Array of objects with `id`, `content`, `sender_role` "
        "('patient'|'staff'), `sender_name`, `recipient_role`, "
        "`recipient_name`, `sent_at`, `read_at`."
    ),
)
def _serialize_message(message: Any) -> dict[str, Any]:
    """Per-row serializer for find_messages."""
    return {
        "id": str(message.id),
        "content": message.content or None,
        "sender_role": _person_role(message.sender),
        "sender_name": _person_name(message.sender),
        "recipient_role": _person_role(message.recipient),
        "recipient_name": _person_name(message.recipient),
        "sent_at": message.created.isoformat() if message.created else None,
        "read_at": message.read.isoformat() if message.read else None,
    }


@standard_tools.filter_search_tool(
    name="find_appointments",
    description=(
        "Search the patient's appointments. Returns each appointment with "
        "`id`, `status`, `start_time` (ISO 8601), `duration_minutes`, "
        "`provider_name`, and `description`. Defaults to upcoming "
        "appointments ordered by start_time ascending; pass "
        "`upcoming_only=false` to include past appointments."
    ),
    queryset_factory=lambda args, pid: Appointment.objects.filter(patient__id=pid),
    filters={
        "status": FilterSpec(
            type="string",
            description=(
                "Filter to a specific appointment progress status. "
                "Values track the workflow from booking to completion: "
                "'unconfirmed' (booked, not yet confirmed), 'attempted', "
                "'confirmed', 'arrived', 'roomed', 'exited' (visit "
                "completed), 'noshowed', 'cancelled'."
            ),
            enum=[s.value for s in AppointmentProgressStatus],
            apply=lambda qs, v: qs.filter(status__iexact=v),
        ),
        "starts_on_or_after": FilterSpec(
            type="string",
            format="date",
            description="ISO 8601 date. Only return appointments with start_time >= this.",
            apply=lambda qs, v: qs.filter(start_time__date__gte=v),
        ),
        "starts_on_or_before": FilterSpec(
            type="string",
            format="date",
            description="ISO 8601 date. Only return appointments with start_time <= this.",
            apply=lambda qs, v: qs.filter(start_time__date__lte=v),
        ),
    },
    ordering=("start_time",),
    select_related=("provider",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=Appointment,
    returns_description=(
        "Array of objects with `id`, `start_time` (ISO 8601), `status`, "
        "`appointment_type`, `provider_name`, `note_type`."
    ),
)
def _serialize_appointment(appointment: Any) -> dict[str, Any]:
    """Per-row serializer for find_appointments."""
    provider = appointment.provider
    provider_name = ""
    if provider is not None:
        first = getattr(provider, "first_name", "") or ""
        last = getattr(provider, "last_name", "") or ""
        provider_name = f"{first} {last}".strip()
    return {
        "id": str(appointment.id),
        "status": appointment.status or None,
        "start_time": appointment.start_time.isoformat() if appointment.start_time else None,
        "duration_minutes": appointment.duration_minutes,
        "provider_name": provider_name or None,
        "description": appointment.description or None,
    }


@standard_tools.filter_search_tool(
    name="find_encounters",
    description=(
        "Search the patient's encounters. Returns each encounter with `id`, "
        "`state`, `medium` (e.g., 'in-person', 'phone', 'telehealth'), "
        "`start_time` (ISO 8601 or null), and `end_time` (ISO 8601 or null). "
        "Defaults to the 25 most-recent encounters ordered by start_time "
        "descending."
    ),
    queryset_factory=lambda args, pid: Encounter.objects.filter(note__patient__id=pid),
    filters={
        "state": FilterSpec(
            type="string",
            description=(
                "Filter to a specific encounter state. Three-letter codes: "
                "'STA' (Started), 'PLA' (Planned), 'CON' (Concluded), "
                "'CAN' (Cancelled)."
            ),
            enum=[s.value for s in EncounterState],
            apply=lambda qs, v: qs.filter(state__iexact=v),
        ),
        "started_on_or_after": FilterSpec(
            type="string",
            format="date",
            description="ISO 8601 date. Only return encounters with start_time >= this.",
            apply=lambda qs, v: qs.filter(start_time__date__gte=v),
        ),
    },
    ordering=("-start_time",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=Encounter,
    returns_description=(
        "Array of objects with `id`, `state` (new|locked|unlocked|...), "
        "`note_type`, `started_at`, `provider_name`."
    ),
)
def _serialize_encounter(encounter: Any) -> dict[str, Any]:
    """Per-row serializer for find_encounters."""
    return {
        "id": str(encounter.id),
        "state": encounter.state or None,
        "medium": encounter.medium or None,
        "start_time": encounter.start_time.isoformat() if encounter.start_time else None,
        "end_time": encounter.end_time.isoformat() if encounter.end_time else None,
    }


# Note state values come from canvas_sdk.v1.data.note.NoteStates (3-letter
# codes — 'NEW', 'LKD', 'ULK', 'SGN', 'DLT', etc.). The canonical current
# state of a note lives in CurrentNoteStateEvent (a view-backed model) —
# Note has no direct state field. find_notes traverses
# `current_state__state` to filter, and reads from `note.current_state`
# at serialize time.
_NOTE_STATE_VALUES = [s.value for s in NoteStates]
# NoteTypeCategories — the canonical category enum on Note.note_type_version.
# (The legacy Note.note_type CharField is empty in current installations;
# real type info lives on the FK to NoteType.)
_NOTE_TYPE_CATEGORY_VALUES = [c.value for c in NoteTypeCategories]
# Goal enum values — surface as JSON-Schema enum on find_goals filters
# so the LLM picks from the canonical set instead of guessing strings
# from a natural-language description.
_GOAL_LIFECYCLE_VALUES = [s.value for s in GoalLifecycleStatus]
_GOAL_ACHIEVEMENT_VALUES = [s.value for s in GoalAchievementStatus]
_GOAL_PRIORITY_VALUES = [s.value for s in GoalPriority]
# AddBannerAlert.Intent is the canonical set ('info' | 'warning' | 'alert').
_BANNER_INTENT_VALUES = ["info", "warning", "alert"]
_CARE_TEAM_MEMBERSHIP_STATUS_VALUES = [s.value for s in CareTeamMembershipStatus]


def _note_current_state(note: Any) -> str | None:
    """Pull the canonical state code off CurrentNoteStateEvent if present.

    ``Note.current_state`` is a reverse OneToOne accessor — it returns
    the related row directly or raises ``DoesNotExist``. Catch the
    miss case to return ``None`` instead of raising.
    """
    try:
        return note.current_state.state
    except Exception:
        return None


def _provider_name(note: Any) -> str | None:
    """Compose a 'First Last' for a Note's provider, or return None."""
    provider = note.provider
    if provider is None:
        return None
    first = getattr(provider, "first_name", "") or ""
    last = getattr(provider, "last_name", "") or ""
    full = f"{first} {last}".strip()
    return full or None


@standard_tools.filter_search_tool(
    name="find_notes",
    description=(
        "Search the patient's notes (encounter documents). Each row has "
        "`id`, `title`, `note_type`, `state` (3-letter code from "
        "NoteStates — e.g. 'NEW' (Created), 'LKD' (Locked), 'ULK' "
        "(Unlocked), 'SGN' (Signed)), `datetime_of_service`, and "
        "`provider_name`. Filter by `state` to find open vs locked notes, "
        "by `note_type` to scope to a category, or by `since` to look at "
        "recent history only. Defaults to most-recent-first."
    ),
    queryset_factory=lambda args, pid: Note.objects.filter(patient__id=pid),
    filters={
        "state": FilterSpec(
            type="string",
            description=(
                "Restrict to notes in a specific lifecycle state. "
                "Three-letter NoteStates code — pick from the enum. "
                "Filters on the canonical current state, not the note's "
                "initial state. Common values: 'NEW' (created/open), "
                "'LKD' (locked), 'ULK' (unlocked), 'SGN' (signed), "
                "'DLT' (deleted)."
            ),
            enum=_NOTE_STATE_VALUES,
            apply=lambda qs, v: qs.filter(current_state__state=v),
        ),
        "note_type": FilterSpec(
            type="string",
            description=(
                "Restrict to notes whose category matches. Broad bucket "
                "from NoteTypeCategories (the canonical category enum). "
                "Common values: 'encounter' (catch-all for in-person / "
                "telehealth / phone / video / home / lab visits), "
                "'inpatient', 'review' (chart review), 'message', "
                "'letter', 'appointment'. For a more specific match like "
                "'Telehealth' vs 'Office visit' (both encounter), use "
                "`note_type_name_contains`."
            ),
            enum=_NOTE_TYPE_CATEGORY_VALUES,
            apply=lambda qs, v: qs.filter(note_type_version__category=v),
        ),
        "note_type_name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the note type's "
                "display name (e.g., 'Telehealth', 'Office visit', "
                "'Chart review', 'Home visit'). More granular than "
                "`note_type` — use to disambiguate within a category."
            ),
            apply=lambda qs, v: qs.filter(note_type_version__name__icontains=v),
        ),
        "since": FilterSpec(
            type="string",
            format="date",
            description=(
                "ISO 8601 date. Only return notes with datetime_of_service >= this value."
            ),
            apply=lambda qs, v: qs.filter(datetime_of_service__gte=v),
        ),
    },
    ordering=("-datetime_of_service",),
    # current_state is a reverse OneToOne (per CurrentNoteStateEvent.note)
    # — use select_related so each row's state is fetched in the same
    # query rather than N+1 lookups during serialization. note_type_version
    # holds the canonical category + display name (Note.note_type is the
    # legacy field and may be empty).
    select_related=("provider", "current_state", "note_type_version"),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=Note,
    returns_description=(
        "Array of objects with `id` (UUID), `dbid` (integer — Canvas-"
        "internal navigation handle), `title`, `note_type` "
        "(NoteTypeCategories enum value — e.g., 'encounter', 'inpatient', "
        "'review'), `note_type_name` (the type's display name — e.g., "
        "'Telehealth', 'Office visit', 'Chart review'), `state` "
        "(NoteStates code or null), `datetime_of_service` (ISO 8601), "
        "`provider_name`."
    ),
)
def _serialize_note(note: Any) -> dict[str, Any]:
    """Per-row serializer for find_notes.

    Includes the Canvas-internal ``dbid`` (integer PK) alongside the
    canonical ``id`` UUID. The dbid is needed by chart-navigation
    primitives in the home-app frontend (e.g., the timeline's
    ``scrollToNoteId`` mechanism, which is integer-keyed). Plugin
    authors should treat dbid as a per-instance navigation handle only
    — not a stable cross-system identifier.

    The ``note_type`` field reads from ``note_type_version.category``
    (NoteTypeCategories) because the legacy ``Note.note_type`` CharField
    is empty in current installations. ``note_type_name`` carries the
    NoteType's display name (e.g., 'Telehealth', 'Office visit') for
    cases where the category alone is too coarse.
    """
    note_type_version = getattr(note, "note_type_version", None)
    return {
        "id": str(note.id),
        "dbid": note.dbid,
        "title": note.title or None,
        "note_type": getattr(note_type_version, "category", None) or None,
        "note_type_name": getattr(note_type_version, "name", None) or None,
        "state": _note_current_state(note),
        "datetime_of_service": (
            note.datetime_of_service.isoformat() if note.datetime_of_service else None
        ),
        "provider_name": _provider_name(note),
    }


@standard_tools.tool(
    name="get_open_note",
    description=(
        "Return metadata for the patient's current open note (the most-"
        "recent note in a mutable state — NEW, UNLOCKED, or CONVERTED). "
        "Use this when the user references 'this note' or 'the open note' "
        "and the agent needs the note_id to drill into it or stage a "
        "command on it. Returns the same row shape as one find_notes "
        "entry, or null if no open note exists."
    ),
    input_schema={"type": "object", "properties": {}},
    categories=("clinical_reads",),
    returns_description=(
        "Object matching find_notes' row shape (`id`, `dbid`, `title`, "
        "`note_type`, `note_type_name`, `state`, `datetime_of_service`, "
        "`provider_name`), or null if the patient has no notes in an "
        "open state."
    ),
)
def _get_open_note(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any] | None:
    """Wrap find_open_note for direct LLM use."""
    patient_id: str = ctx["patient_id"]
    note = find_open_note(patient_id)
    if note is None:
        return None
    return _serialize_note(note)


def _walk_note_body(body: Any) -> list[tuple[str, dict[str, Any]]]:
    """Walk a note's body in document order.

    Each item in the body is either a text block (free narrative the
    clinician typed between commands) or a command marker (a reference
    to a row in the Command table by command_uuid). We return the
    sequence in order so callers can preserve note-reading flow.
    Empty text blocks are skipped.

    Returns a list of (kind, payload) tuples where kind is "text" or
    "command".
    """
    if not isinstance(body, list):
        return []
    out: list[tuple[str, dict[str, Any]]] = []
    for item in body:
        if not isinstance(item, dict):
            continue
        kind = item.get("type")
        if kind == "text":
            value = item.get("value") or ""
            if value.strip():
                out.append(("text", {"value": value}))
        elif kind == "command":
            data = item.get("data") or {}
            uuid = data.get("command_uuid")
            if uuid:
                out.append(("command", {"uuid": str(uuid), "schema_key": item.get("value")}))
    return out


@standard_tools.tool(
    name="get_note_content",
    description=(
        "Read the contents of a specific note in document order — the "
        "free-text narrative the clinician typed interleaved with the "
        "structured clinical commands they committed (Plan, Assess, "
        "Diagnose, Prescribe, LabOrder, etc.). Use this when the user "
        "asks about a specific note ('what's in this note?', 'did "
        "today's visit address X?', 'summarize the assessment') so the "
        "agent can answer without the clinician having to re-read the "
        "note themselves. Skips entered-in-error commands and empty "
        "text blocks. Patient scope is enforced — a note belonging to "
        "a different patient returns null."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "note_id": {
                "type": "string",
                "description": (
                    "UUID of the note to read. From a prior find_notes or "
                    "get_open_note call (the row's `id` field)."
                ),
            },
        },
        "required": ["note_id"],
    },
    categories=("clinical_reads",),
    returns_description=(
        "Object with the note's metadata (`id`, `dbid`, `title`, `note_type`, "
        "`note_type_name`, `state`, `datetime_of_service`, `provider_name`) plus a "
        "`content` array of items in document order. Each item is "
        "either `{type: 'text', value: <free-text>}` (the clinician's "
        "narrative between commands) or `{type: 'command', uuid, "
        "schema_key, state, data}` (a structured chart command — "
        "schema_key like 'plan'/'assess'/'labOrder', data containing "
        "the command-specific fields). Returns null if no note with "
        "that id exists for the current patient."
    ),
)
def _get_note_content(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any] | None:
    """Return a note's content in document order, patient-scope enforced.

    The note is looked up by id AND patient — a request for a note that
    belongs to a different patient is indistinguishable from a request
    for a nonexistent note (both return None). This prevents cross-
    patient leakage even if the model hallucinates a note_id.

    Two-pass: walk the body once to collect referenced command UUIDs
    (preserving document order), then bulk-fetch the Command rows in
    one query (skipping entered-in-error). Final emit interleaves
    text + command items the way the clinician wrote them.
    """
    note_id = arguments["note_id"]
    patient_id: str = ctx["patient_id"]

    note = (
        Note.objects.filter(id=note_id, patient__id=patient_id)
        .select_related("provider", "current_state")
        .first()
    )
    if note is None:
        return None

    walked = _walk_note_body(note.body)
    command_uuids = [payload["uuid"] for kind, payload in walked if kind == "command"]
    commands_by_uuid: dict[str, Any] = {
        str(c.id): c
        for c in Command.objects.filter(note=note, id__in=command_uuids).exclude(
            state="entered_in_error"
        )
    }

    content: list[dict[str, Any]] = []
    for kind, payload in walked:
        if kind == "text":
            content.append({"type": "text", "value": payload["value"]})
            continue
        cmd = commands_by_uuid.get(payload["uuid"])
        if cmd is None:
            # Command was entered-in-error or otherwise missing — skip
            # silently. The body still references it but the agent
            # doesn't need to know about deleted entries.
            continue
        content.append(
            {
                "type": "command",
                "uuid": str(cmd.id),
                "schema_key": cmd.schema_key,
                "state": cmd.state or None,
                "data": cmd.data or {},
            }
        )

    return {**_serialize_note(note), "content": content}


@standard_tools.filter_search_tool(
    name="find_goals",
    description=(
        "Search the patient's care-plan goals. Returns each goal with "
        "`goal_statement`, `lifecycle_status` (e.g., 'active', 'completed', "
        "'cancelled'), `achievement_status` (e.g., 'in-progress', "
        "'achieved'), `priority` ('high-priority', 'medium-priority', "
        "'low-priority'), `start_date` (ISO 8601 or null), `due_date` "
        "(ISO 8601 or null), and `progress` (free-text note). Defaults to "
        "active goals ordered by most-recent start_date."
    ),
    queryset_factory=lambda args, pid: Goal.objects.filter(patient__id=pid),
    filters={
        "statement_contains": FilterSpec(
            type="string",
            description="Case-insensitive substring match on the goal_statement text.",
            apply=lambda qs, v: qs.filter(goal_statement__icontains=v),
        ),
        "lifecycle_status": FilterSpec(
            type="string",
            description=(
                "Filter to a specific GoalLifecycleStatus value (e.g., "
                "'active', 'completed', 'cancelled')."
            ),
            enum=_GOAL_LIFECYCLE_VALUES,
            apply=lambda qs, v: qs.filter(lifecycle_status=v),
        ),
        "achievement_status": FilterSpec(
            type="string",
            description=(
                "Filter to a specific GoalAchievementStatus value (e.g., "
                "'in-progress', 'achieved', 'not-achieved')."
            ),
            enum=_GOAL_ACHIEVEMENT_VALUES,
            apply=lambda qs, v: qs.filter(achievement_status=v),
        ),
        "priority": FilterSpec(
            type="string",
            description=(
                "Filter to a specific GoalPriority value ('high-priority', "
                "'medium-priority', 'low-priority')."
            ),
            enum=_GOAL_PRIORITY_VALUES,
            apply=lambda qs, v: qs.filter(priority=v),
        ),
    },
    ordering=("-start_date",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=Goal,
    returns_description=(
        "Array of objects with `id`, `goal_statement`, `lifecycle_status`, "
        "`achievement_status`, `priority`, `start_date`, `due_date`."
    ),
)
def _serialize_goal(goal: Any) -> dict[str, Any]:
    """Per-row serializer for find_goals."""
    return {
        "id": str(goal.id),
        "goal_statement": goal.goal_statement or None,
        "lifecycle_status": goal.lifecycle_status or None,
        "achievement_status": goal.achievement_status or None,
        "priority": goal.priority or None,
        "start_date": goal.start_date.isoformat() if goal.start_date else None,
        "due_date": goal.due_date.isoformat() if goal.due_date else None,
        "progress": goal.progress or None,
    }


@standard_tools.filter_search_tool(
    name="find_imaging_reports",
    description=(
        "Search the patient's imaging reports. Returns each report with "
        "`id`, `name` (test or modality, e.g., 'Chest X-ray'), "
        "`assigned_date` (ISO 8601 or null), `source` (e.g., 'internal', "
        "'external'), and `requires_signature` (bool). Patient scope is "
        "enforced and junked reports are excluded. Defaults to the 25 "
        "most-recent reports."
    ),
    queryset_factory=lambda args, pid: ImagingReport.objects.filter(patient__id=pid, junked=False),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the report name "
                "(e.g., 'chest', 'mammo', 'mri')."
            ),
            apply=lambda qs, v: qs.filter(name__icontains=v),
        ),
        "assigned_on_or_after": FilterSpec(
            type="string",
            format="date",
            description=("ISO 8601 date. Only return reports with assigned_date >= this value."),
            apply=lambda qs, v: qs.filter(assigned_date__date__gte=v),
        ),
    },
    ordering=("-assigned_date",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=ImagingReport,
    returns_description=(
        "Array of objects with `id`, `name`, `result_status`, `assigned_at`, `narrative`."
    ),
)
def _serialize_imaging_report(report: Any) -> dict[str, Any]:
    """Per-row serializer for find_imaging_reports."""
    return {
        "id": str(report.id),
        "name": report.name or None,
        "assigned_date": report.assigned_date.isoformat() if report.assigned_date else None,
        "source": report.source or None,
        "requires_signature": bool(report.requires_signature),
    }


@standard_tools.filter_search_tool(
    name="find_referrals",
    description=(
        "Search the patient's outgoing referrals. Returns each referral with "
        "`id`, `clinical_question`, `priority`, `notes` (free-text), "
        "`date_referred` (ISO 8601), `service_provider_name`, and "
        "`forwarded` (bool). Ordered most-recent first."
    ),
    queryset_factory=lambda args, pid: Referral.objects.filter(patient__id=pid),
    filters={
        "question_contains": FilterSpec(
            type="string",
            description=("Case-insensitive substring match on the clinical_question field."),
            apply=lambda qs, v: qs.filter(clinical_question__icontains=v),
        ),
        "priority": FilterSpec(
            type="string",
            description=(
                "Filter to a specific priority (free-text on Referral; values "
                "depend on the customer's configuration). Case-insensitive."
            ),
            apply=lambda qs, v: qs.filter(priority__iexact=v),
        ),
        "referred_on_or_after": FilterSpec(
            type="string",
            format="date",
            description=("ISO 8601 date. Only return referrals with date_referred >= this."),
            apply=lambda qs, v: qs.filter(date_referred__date__gte=v),
        ),
    },
    ordering=("-date_referred",),
    select_related=("service_provider",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=Referral,
    returns_description=(
        "Array of objects with `id`, `service_provider_name`, "
        "`clinical_question`, `priority`, `status`, `originated_at`."
    ),
)
def _serialize_referral(referral: Any) -> dict[str, Any]:
    """Per-row serializer for find_referrals."""
    provider = referral.service_provider
    provider_name = ""
    if provider is not None:
        # ServiceProvider's exact field set varies; try common names.
        first = getattr(provider, "first_name", "") or ""
        last = getattr(provider, "last_name", "") or ""
        provider_name = f"{first} {last}".strip() or getattr(provider, "name", "") or ""
    return {
        "id": str(referral.id),
        "clinical_question": referral.clinical_question or None,
        "priority": referral.priority or None,
        "notes": referral.notes or None,
        "date_referred": (referral.date_referred.isoformat() if referral.date_referred else None),
        "service_provider_name": provider_name or None,
        "forwarded": bool(referral.forwarded),
    }


@standard_tools.filter_search_tool(
    name="find_care_team_members",
    description=(
        "Return the staff members on the patient's care team. Each result has "
        "`staff_name`, `role_display` (e.g., 'Primary Care Provider', "
        "'Care Manager'), `role_code`, `status` (e.g., 'active', 'inactive'), "
        "and `is_lead` (true for the patient's primary contact). Ordered with "
        "the lead member first, then by role."
    ),
    queryset_factory=lambda args, pid: CareTeamMembership.objects.filter(patient__id=pid),
    filters={
        "role_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on role_display (e.g., 'primary', 'manager')."
            ),
            apply=lambda qs, v: qs.filter(role_display__icontains=v),
        ),
        "status": FilterSpec(
            type="string",
            description=(
                "Filter to a specific CareTeamMembershipStatus value (e.g., "
                "'active', 'inactive', 'suspended', 'proposed')."
            ),
            enum=_CARE_TEAM_MEMBERSHIP_STATUS_VALUES,
            apply=lambda qs, v: qs.filter(status=v),
        ),
    },
    ordering=("-lead", "role_display"),
    select_related=("staff",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=CareTeamMembership,
    returns_description=("Array of objects with `id`, `staff_name`, `role`, `lead`, `status`."),
)
def _serialize_care_team_member(membership: Any) -> dict[str, Any]:
    """Per-row serializer for find_care_team_members."""
    staff = membership.staff
    staff_name = ""
    if staff is not None:
        first = getattr(staff, "first_name", "") or ""
        last = getattr(staff, "last_name", "") or ""
        staff_name = f"{first} {last}".strip()
    return {
        "id": str(membership.id),
        "staff_name": staff_name or None,
        "role_display": membership.role_display or None,
        "role_code": membership.role_code or None,
        "status": membership.status or None,
        "is_lead": bool(membership.lead),
    }


@standard_tools.filter_search_tool(
    name="find_note_types",
    description=(
        "List the customer's configured NoteType rows. Returns each type with "
        "`id` (the UUID to pass as `note_type_id` to note-creation tools), "
        "`name` (display name shown in the UI), `category` (NoteTypeCategories "
        "enum value: 'encounter', 'review', 'data', 'task', 'inpatient', "
        "'letter', 'message', 'appointment', 'schedule_event', 'ccda'), "
        "`is_active`, and `is_visible`. Customer-level config — NOT patient-scoped; "
        "the patient_id on ctx is ignored. Use to resolve a friendly handle "
        "('chart review note', 'office visit') into the UUID note-write tools "
        "need."
    ),
    queryset_factory=lambda args, pid: NoteType.objects.all(),
    filters={
        "category": FilterSpec(
            type="string",
            description=(
                "Restrict to a single NoteTypeCategories value — e.g. 'review' "
                "for chart-review notes, 'encounter' for visit notes, 'letter' "
                "for letters."
            ),
            enum=_NOTE_TYPE_CATEGORY_VALUES,
            apply=lambda qs, v: qs.filter(category=v),
        ),
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the type's display name "
                "(e.g. 'review', 'telehealth', 'office')."
            ),
            apply=lambda qs, v: qs.filter(name__icontains=v),
        ),
        "active_only": FilterSpec(
            type="boolean",
            description=(
                "When true (default), restrict to currently active types "
                "(is_active and is_visible). Set false to include deprecated or "
                "hidden types."
            ),
            apply=lambda qs, v: qs.filter(is_active=True, is_visible=True) if v else qs,
        ),
    },
    ordering=("rank", "name"),
    limit_default=50,
    limit_max=200,
    limit_description="Maximum results. Defaults to 50.",
    categories=("config_reads",),
    model=NoteType,
    returns_description=(
        "Array of objects with `id`, `name`, `category` (NoteTypeCategories), "
        "`is_active`, `is_visible`, `is_billable`, `is_sig_required`."
    ),
)
def _serialize_note_type(note_type: Any) -> dict[str, Any]:
    """Per-row serializer for find_note_types."""
    return {
        "id": str(note_type.id),
        "name": note_type.name or None,
        "category": note_type.category or None,
        "is_active": bool(note_type.is_active),
        "is_visible": bool(note_type.is_visible),
        "is_billable": bool(note_type.is_billable),
        "is_sig_required": bool(note_type.is_sig_required),
    }


@standard_tools.filter_search_tool(
    name="find_practice_locations",
    description=(
        "List the customer's configured PracticeLocation rows. Returns each "
        "location with `id` (the UUID to pass as `practice_location_id` to "
        "note-creation tools), `full_name`, `short_name`, `place_of_service_code` "
        "(CMS POS code), and `active`. Customer-level config — NOT patient-scoped. "
        "Use to resolve a friendly handle ('main clinic', 'downtown office') "
        "into the UUID note-write tools need."
    ),
    queryset_factory=lambda args, pid: PracticeLocation.objects.all(),
    filters={
        "active_only": FilterSpec(
            type="boolean",
            description="When true (default), restrict to active locations.",
            apply=lambda qs, v: qs.filter(active=True) if v else qs,
        ),
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on full_name (e.g. 'main', 'downtown')."
            ),
            apply=lambda qs, v: qs.filter(full_name__icontains=v),
        ),
    },
    ordering=("full_name",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results. Defaults to 25.",
    categories=("config_reads",),
    model=PracticeLocation,
    returns_description=(
        "Array of objects with `id`, `full_name`, `short_name`, `place_of_service_code`, `active`."
    ),
)
def _serialize_practice_location(loc: Any) -> dict[str, Any]:
    """Per-row serializer for find_practice_locations."""
    return {
        "id": str(loc.id),
        "full_name": loc.full_name or None,
        "short_name": loc.short_name or None,
        "place_of_service_code": loc.place_of_service_code or None,
        "active": bool(loc.active),
    }


@standard_tools.filter_search_tool(
    name="find_lab_partners",
    description=(
        "List the customer's configured lab partners (LabCorp, Quest, "
        "in-house, etc.). Returns each with `id` (UUID to pass as "
        "`lab_partner` to `originate_lab_order`), `name`, `active`, and "
        "`electronic_ordering_enabled`. Customer-level config — NOT "
        "patient-scoped. Step 1 of the order-lab flow: pick a partner here, "
        "then call `find_lab_partner_tests(lab_partner_id=<id>)` to "
        "discover the orderable tests for that partner."
    ),
    queryset_factory=lambda args, pid: LabPartner.objects.all(),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the partner's name "
                "(e.g. 'labcorp', 'quest', 'generic')."
            ),
            apply=lambda qs, v: qs.filter(name__icontains=v),
        ),
        "active_only": FilterSpec(
            type="boolean",
            description=("When true (default), restrict to active partners."),
            apply=lambda qs, v: qs.filter(active=True) if v else qs,
        ),
        "electronic_ordering_only": FilterSpec(
            type="boolean",
            description=(
                "When true, restrict to partners that accept electronic orders "
                "(filters out paper-only partners)."
            ),
            apply=lambda qs, v: qs.filter(electronic_ordering_enabled=True) if v else qs,
        ),
    },
    ordering=("name",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results. Defaults to 25.",
    categories=("config_reads",),
    model=LabPartner,
    returns_description=(
        "Array of objects with `id`, `name`, `active`, `electronic_ordering_enabled`."
    ),
)
def _serialize_lab_partner(partner: Any) -> dict[str, Any]:
    """Per-row serializer for find_lab_partners."""
    return {
        "id": str(partner.id),
        "name": partner.name or None,
        "active": bool(partner.active),
        "electronic_ordering_enabled": bool(partner.electronic_ordering_enabled),
    }


def _lab_partner_tests_queryset(args: dict[str, Any], pid: str) -> Any:
    """Resolve lab_partner (UUID or name) and scope to its available tests.

    Without scoping by partner the result set is huge (every customer's
    test compendium combined) and the UUIDs the agent picks may belong to
    a partner the customer isn't ordering from. We treat partner scoping
    as required.
    """
    partner_id = args.get("lab_partner_id")
    partner_name = args.get("lab_partner_name")
    if not (partner_id or partner_name):
        return LabPartnerTest.objects.none()

    if partner_id:
        return LabPartnerTest.objects.filter(lab_partner__id=partner_id)
    return LabPartnerTest.objects.filter(lab_partner__name__iexact=partner_name)


@standard_tools.filter_search_tool(
    name="find_lab_partner_tests",
    description=(
        "Search a lab partner's compendium of orderable tests. Returns each "
        "test with `id` (UUID) and `order_code` (the partner's own catalog "
        "code) — EITHER value is accepted by `originate_lab_order`'s "
        "`tests_order_codes` argument. Also returns `order_name` (display "
        "name) and `cpt_code`. Customer-level config — NOT patient-scoped. "
        "EXACTLY ONE of `lab_partner_id` or `lab_partner_name` is required "
        "to scope the search; without it the result set is empty. Workflow: "
        "(1) `find_lab_partners` to choose a partner; (2) "
        "`find_lab_partner_tests(lab_partner_id=<id>, search='glucose')` "
        "to find tests; (3) `originate_lab_order(lab_partner=<id>, "
        "tests_order_codes=[<order_code>, ...])`."
    ),
    queryset_factory=_lab_partner_tests_queryset,
    filters={
        "lab_partner_id": FilterSpec(
            type="string",
            description=(
                "UUID of the lab partner whose tests to search — from "
                "`find_lab_partners`. Either this or `lab_partner_name`."
            ),
            # Consumed by queryset_factory; no apply.
        ),
        "lab_partner_name": FilterSpec(
            type="string",
            description=(
                "Case-insensitive exact name of the lab partner — alternative "
                "to `lab_partner_id`. Either this or `lab_partner_id`."
            ),
            # Consumed by queryset_factory; no apply.
        ),
        "search": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match across `order_name`, "
                "`order_code`, and `keywords` — same shape as the chart-UI "
                "autocomplete (e.g. 'glucose', 'CBC', 'lipid')."
            ),
            apply=lambda qs, v: qs.filter(
                Q(order_name__icontains=v) | Q(order_code__icontains=v) | Q(keywords__icontains=v)
            ),
        ),
        "cpt_contains": FilterSpec(
            type="string",
            description="Case-insensitive substring match on the test's CPT code.",
            apply=lambda qs, v: qs.filter(cpt_code__icontains=v),
        ),
    },
    ordering=("order_name",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results. Defaults to 25.",
    categories=("config_reads",),
    model=LabPartnerTest,
    returns_description=("Array of objects with `id`, `order_code`, `order_name`, `cpt_code`."),
)
def _serialize_lab_partner_test(test: Any) -> dict[str, Any]:
    """Per-row serializer for find_lab_partner_tests."""
    return {
        "id": str(test.id),
        "order_code": test.order_code or None,
        "order_name": test.order_name or None,
        "cpt_code": test.cpt_code or None,
    }


@standard_tools.filter_search_tool(
    name="find_medication_statements",
    description=(
        "Search the patient's recorded medication statements — patient-reported "
        "or self-administered medications (distinct from active prescriptions "
        "which `find_medications` covers). Returns each statement with "
        "`medication_name`, `start_date` (ISO 8601 or null), `end_date` (ISO "
        "8601 or null), `dose_form`, `dose_route`, `dose_frequency_interval`, "
        "and `sig_original_input` (the patient's verbatim sig)."
    ),
    queryset_factory=lambda args, pid: MedicationStatement.objects.filter(patient__id=pid),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the medication's first-coding display."
            ),
            apply=lambda qs, v: qs.filter(medication__codings__display__icontains=v),
        ),
        "started_on_or_after": FilterSpec(
            type="string",
            format="date",
            description="ISO 8601 date. Only return statements with start_date >= this.",
            apply=lambda qs, v: qs.filter(start_date__gte=v),
        ),
    },
    ordering=("-start_date",),
    select_related=("medication",),
    prefetch_related=("medication__codings",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=MedicationStatement,
    returns_description=(
        "Array of objects with `id`, `medication_name`, `narrative`, `recorded_at`."
    ),
)
def _serialize_medication_statement(statement: Any) -> dict[str, Any]:
    """Per-row serializer for find_medication_statements."""
    medication = statement.medication
    medication_name = ""
    if medication is not None:
        coding = medication.codings.first()
        if coding is not None:
            medication_name = coding.display or ""
    return {
        "id": str(statement.id),
        "medication_name": medication_name or "(unknown)",
        "start_date": statement.start_date.isoformat() if statement.start_date else None,
        "end_date": statement.end_date.isoformat() if statement.end_date else None,
        "dose_form": statement.dose_form or None,
        "dose_route": statement.dose_route or None,
        "dose_frequency_interval": statement.dose_frequency_interval or None,
        "sig_original_input": statement.sig_original_input or None,
    }


@standard_tools.filter_search_tool(
    name="find_external_events",
    description=(
        "Search external healthcare events recorded for the patient — typically "
        "HL7 feeds from external systems (ADT, ORM, etc.). Each event has "
        "`event_type` (e.g., 'ADT', 'ORM'), `event_datetime` (ISO 8601), "
        "`facility_name` (from the linked external visit), and "
        "`information_source`. Useful for understanding the patient's "
        "encounters outside the EHR. Ordered most-recent first."
    ),
    queryset_factory=lambda args, pid: ExternalEvent.objects.filter(patient__id=pid),
    filters={
        "event_type": FilterSpec(
            type="string",
            description=(
                "Filter to a specific event_type (e.g., 'ADT' for admit/discharge/"
                "transfer, 'ORM' for orders). Case-insensitive exact match."
            ),
            apply=lambda qs, v: qs.filter(event_type__iexact=v),
        ),
        "occurred_on_or_after": FilterSpec(
            type="string",
            format="date",
            description=("ISO 8601 date. Only return events with event_datetime >= this."),
            apply=lambda qs, v: qs.filter(event_datetime__date__gte=v),
        ),
    },
    ordering=("-event_datetime",),
    select_related=("external_visit",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=ExternalEvent,
    returns_description=(
        "Array of objects with `id`, `event_type`, `event_datetime`, "
        "`facility_name`, `information_source`."
    ),
)
def _serialize_external_event(event: Any) -> dict[str, Any]:
    """Per-row serializer for find_external_events."""
    visit = event.external_visit
    facility_name = getattr(visit, "facility_name", "") if visit else ""
    return {
        "id": str(event.id),
        "event_type": event.event_type or None,
        "event_datetime": event.event_datetime.isoformat() if event.event_datetime else None,
        "facility_name": facility_name or None,
        "information_source": (getattr(visit, "information_source", "") if visit else "") or None,
    }


@standard_tools.filter_search_tool(
    name="find_prescriptions",
    description=(
        "Search the patient's prescription records (actual Rx events — "
        "distinct from `find_medications` which surfaces the medication "
        "list). Each result has `medication_name`, `status`, `written_date` "
        "(ISO 8601), `dispensed_date` (ISO 8601 or null), `end_date` (ISO "
        "8601 or null), `sig_original_input`, `dose_form`, `dose_route`, "
        "`dose_frequency_interval`, and `is_refill`. Patient scope is "
        "enforced. Defaults to committed prescriptions ordered "
        "most-recent first."
    ),
    queryset_factory=lambda args, pid: Prescription.objects.committed().filter(patient__id=pid),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the medication's first-coding display."
            ),
            apply=lambda qs, v: qs.filter(medication__codings__display__icontains=v),
        ),
        "status": FilterSpec(
            type="string",
            description=(
                "Filter to a specific prescription status (e.g., 'active', "
                "'completed', 'cancelled'). Case-insensitive."
            ),
            apply=lambda qs, v: qs.filter(status__iexact=v),
        ),
        "written_on_or_after": FilterSpec(
            type="string",
            format="date",
            description="ISO 8601 date. Only return prescriptions with written_date >= this.",
            apply=lambda qs, v: qs.filter(written_date__date__gte=v),
        ),
    },
    ordering=("-written_date",),
    select_related=("medication",),
    prefetch_related=("medication__codings",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=Prescription,
    returns_description=(
        "Array of objects with `id`, `medication_name`, `status`, "
        "`written_date`, `dispensed_date`, `quantity_to_dispense`, "
        "`days_supply`, `is_refill`, `sig_original_input`."
    ),
)
def _serialize_prescription(prescription: Any) -> dict[str, Any]:
    """Per-row serializer for find_prescriptions."""
    medication = prescription.medication
    medication_name = ""
    if medication is not None:
        coding = medication.codings.first()
        if coding is not None:
            medication_name = coding.display or ""
    return {
        "id": str(prescription.id),
        "medication_name": medication_name or "(unknown)",
        "status": prescription.status or None,
        "written_date": (
            prescription.written_date.isoformat() if prescription.written_date else None
        ),
        "dispensed_date": (
            prescription.dispensed_date.isoformat() if prescription.dispensed_date else None
        ),
        "end_date": prescription.end_date.isoformat() if prescription.end_date else None,
        "sig_original_input": prescription.sig_original_input or None,
        "dose_form": prescription.dose_form or None,
        "dose_route": prescription.dose_route or None,
        "dose_frequency_interval": prescription.dose_frequency_interval or None,
        "is_refill": bool(prescription.is_refill),
    }


@standard_tools.filter_search_tool(
    name="find_questionnaire_responses",
    description=(
        "Search the patient's completed and in-progress questionnaire "
        "responses (Interviews). Each result includes `name`, "
        "`progress_status`, `questionnaire_names`, `answered_at` (ISO "
        "8601), and `responses` — an array of per-question answers with "
        "the question text, the human-readable selection, and "
        "`response_value` (the question option's underlying value string, "
        "often numeric for scored instruments like PHQ-9 or Stress). For "
        "scored questionnaires `response_value` is what you'd chart or "
        "sum. For non-scored / categorical ones it may be text — in that "
        "case offer the clinician a numeric conversion before plotting "
        "and confirm their interpretation before treating it as a score. "
        "Patient scope is enforced; non-committed interviews are excluded."
    ),
    queryset_factory=lambda args, pid: Interview.objects.committed().filter(patient__id=pid),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the interview's name "
                "(e.g., 'PHQ', 'depression', 'GAD', 'stress')."
            ),
            apply=lambda qs, v: qs.filter(name__icontains=v),
        ),
        "progress_status": FilterSpec(
            type="string",
            description=(
                "Filter to a specific progress_status code (e.g., 'F' for "
                "finished/complete, 'S' for started, 'N' for new). "
                "Case-insensitive."
            ),
            apply=lambda qs, v: qs.filter(progress_status__iexact=v),
        ),
    },
    ordering=("-modified",),
    prefetch_related=(
        "questionnaires",
        "interview_responses",
        "interview_responses__question",
        "interview_responses__response_option",
    ),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=Interview,
    returns_description=(
        "Array of objects with `id`, `name`, `progress_status`, "
        "`questionnaire_names`, `answered_at`, and `responses` "
        "(per-question array of `question`, `response_text`, "
        "`response_value`)."
    ),
)
def _serialize_interview(interview: Any) -> dict[str, Any]:
    """Per-row serializer for find_questionnaire_responses.

    Surfaces the per-question response array so the agent can read the
    actual answers (and, for scored instruments, the numeric value). The
    underlying `InterviewQuestionResponse.response_option_value` is a
    free-text field that customers populate with whatever scale the
    questionnaire defines — typically "1"-"4" or "0"-"3" for Likert
    instruments, but the agent should treat it as a string and confirm
    interpretation with the clinician before charting.
    """
    questionnaire_names = [
        q.name for q in interview.questionnaires.all() if getattr(q, "name", None)
    ]
    responses = []
    for r in interview.interview_responses.all():
        question_text = getattr(getattr(r, "question", None), "name", None) or None
        response_text = getattr(getattr(r, "response_option", None), "name", None) or None
        responses.append(
            {
                "question": question_text,
                "response_text": response_text,
                "response_value": r.response_option_value or None,
            }
        )
    answered_at = getattr(interview, "modified", None)
    return {
        "id": str(interview.id),
        "name": interview.name or None,
        "status": interview.status or None,
        "progress_status": interview.progress_status or None,
        "questionnaire_names": questionnaire_names,
        "answered_at": answered_at.isoformat() if answered_at else None,
        "responses": responses,
    }


@standard_tools.filter_search_tool(
    name="find_stop_medication_events",
    description=(
        "Search records of medications the patient stopped. Each event has "
        "`medication_name`, `rationale` (free-text reason for stopping, "
        "captured by the clinician), and `stopped_at` (ISO 8601). Useful "
        "for understanding why a medication is no longer active. Ordered "
        "most-recent first."
    ),
    queryset_factory=lambda args, pid: StopMedicationEvent.objects.filter(
        patient__id=pid, deleted=False
    ),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the stopped medication's first-coding display."
            ),
            apply=lambda qs, v: qs.filter(medication__codings__display__icontains=v),
        ),
        "rationale_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the rationale text "
                "(e.g., 'side effects', 'ineffective', 'allergy')."
            ),
            apply=lambda qs, v: qs.filter(rationale__icontains=v),
        ),
    },
    ordering=("-created",),
    select_related=("medication",),
    prefetch_related=("medication__codings",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=StopMedicationEvent,
    returns_description=(
        "Array of objects with `id`, `medication_name`, `rationale`, `stopped_at`."
    ),
)
def _serialize_stop_med_event(event: Any) -> dict[str, Any]:
    """Per-row serializer for find_stop_medication_events."""
    medication = event.medication
    medication_name = ""
    if medication is not None:
        coding = medication.codings.first()
        if coding is not None:
            medication_name = coding.display or ""
    return {
        "id": str(event.id),
        "medication_name": medication_name or "(unknown)",
        "rationale": event.rationale or None,
        "stopped_at": event.created.isoformat() if event.created else None,
    }


@standard_tools.filter_search_tool(
    name="find_banner_alerts",
    description=(
        "Search the patient's banner alerts (visual flags shown on the chart). "
        "Returns each banner's `key`, `narrative`, `intent` (info/warning/"
        "alert), `placement` (list), `href` (or null), and `status` "
        "(active/inactive). Use this to discover what's already flagged "
        "before adding a duplicate, or to find a banner's key for "
        "`remove_banner_alert`. Defaults to active banners only."
    ),
    queryset_factory=lambda args, pid: (
        BannerAlert.objects.filter(patient__id=pid)
        if args.get("include_inactive")
        else BannerAlert.objects.filter(patient__id=pid, status="active")
    ),
    filters={
        "narrative_contains": FilterSpec(
            type="string",
            description=(
                "Case-insensitive substring match on the banner's narrative text "
                "(e.g., 'mammogram', 'INR')."
            ),
            apply=lambda qs, v: qs.filter(narrative__icontains=v),
        ),
        "intent": FilterSpec(
            type="string",
            description=("Restrict to one visual intent: 'info', 'warning', or 'alert'."),
            enum=_BANNER_INTENT_VALUES,
            apply=lambda qs, v: qs.filter(intent=v),
        ),
        "include_inactive": FilterSpec(
            type="boolean",
            description=(
                "When true, also return banners with status='inactive' "
                "(historical/removed). Default false — active only."
            ),
            # Consumed by queryset_factory.
        ),
    },
    ordering=("-created",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=BannerAlert,
    returns_description=(
        "Array of objects with `key`, `narrative`, `intent`, `placement` "
        "(array of strings), `href`, `status`."
    ),
)
def _serialize_banner_alert(banner: Any) -> dict[str, Any]:
    """Per-row serializer for find_banner_alerts."""
    return {
        "key": banner.key,
        "narrative": banner.narrative,
        "intent": banner.intent,
        "placement": list(banner.placement) if banner.placement else [],
        "href": banner.href or None,
        "status": banner.status,
    }


@standard_tools.filter_search_tool(
    name="find_protocol_cards",
    description=(
        "Search the patient's protocol cards (clinical decision support "
        "surfaces shown on the chart). Each card has a `protocol_key` "
        "(pass to `add_or_update_protocol_card` as `card_key` to update "
        "it), `title`, `narrative`, `status` (due / satisfied / "
        "not_applicable / pending / not_relevant), and `plugin_name` "
        "identifying which plugin staged it. Use this to discover what's "
        "already flagged before adding a new card, to find prior cards "
        "your plugin staged that need a status update, or to inspect "
        "cards staged by other plugins for context. Defaults to all "
        "statuses; filter to active ones via `active_only=true`."
    ),
    queryset_factory=lambda args, pid: (
        ProtocolCurrent.objects.filter(
            patient__id=pid,
            status__in=("due", "pending"),
        )
        if args.get("active_only")
        else ProtocolCurrent.objects.filter(patient__id=pid)
    ),
    filters={
        "title_contains": FilterSpec(
            type="string",
            description="Case-insensitive substring match on the card's title.",
            apply=lambda qs, v: qs.filter(title__icontains=v),
        ),
        "status": FilterSpec(
            type="string",
            description=(
                "Restrict to one lifecycle status: 'due', 'satisfied', "
                "'not_applicable', 'pending', 'not_relevant'."
            ),
            apply=lambda qs, v: qs.filter(status=v),
        ),
        "plugin_name": FilterSpec(
            type="string",
            description=(
                "Restrict to cards staged by a specific plugin (exact match). "
                "Use to scope find results to your own plugin's cards."
            ),
            apply=lambda qs, v: qs.filter(plugin_name=v),
        ),
        "active_only": FilterSpec(
            type="boolean",
            description=(
                "When true, return only cards with status='due' or 'pending'. "
                "Default false — return cards in any status."
            ),
            # Consumed by queryset_factory.
        ),
    },
    ordering=("-created",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results to return. Defaults to 25.",
    categories=("clinical_reads",),
    model=ProtocolCurrent,
    returns_description=(
        "Array of objects with `protocol_key`, `title`, `narrative`, "
        "`status`, `plugin_name`, `next_review` (ISO 8601 or null), "
        "`snoozed`."
    ),
)
def _serialize_protocol_card(card: Any) -> dict[str, Any]:
    """Per-row serializer for find_protocol_cards."""
    return {
        "protocol_key": card.protocol_key,
        "title": card.title,
        "narrative": card.narrative,
        "status": card.status,
        "plugin_name": card.plugin_name or None,
        "next_review": card.next_review.isoformat() if card.next_review else None,
        "snoozed": bool(card.snoozed),
    }


# get_patient_demographics is a scalar read (returns one dict, not a list)
# and doesn't fit the filter-search shape — hand-registered via the base
# `tool` decorator.
@standard_tools.tool(
    name="get_patient_demographics",
    description=(
        "Return basic demographics for the current patient: legal name, "
        "preferred name, MRN, date of birth, computed age in years, "
        "sex_at_birth, gender_identity, preferred_pronouns, and whether "
        "they're marked deceased. Takes no arguments."
    ),
    input_schema={"type": "object", "properties": {}},
    categories=("clinical_reads",),
    returns_description=(
        "Object with `first_name`, `middle_name`, `last_name`, "
        "`preferred_name`, `mrn`, `birth_date`, `age_years`, "
        "`sex_at_birth`, `gender_identity`, `preferred_pronouns`, "
        "`deceased`."
    ),
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


# ---------------------------------------------------------------------------
# Write tools — stage clinician-reviewable actions
# ---------------------------------------------------------------------------


_BANNER_PLACEMENTS = [p.value for p in AddBannerAlert.Placement]
_BANNER_INTENTS = [i.value for i in AddBannerAlert.Intent]


standard_tools.add_effect_tool(
    name="add_banner_alert",
    description=(
        "Surface a banner alert on the patient — visible to anyone viewing "
        "the chart. Use to flag clinically meaningful state the clinician "
        "should notice on their next visit (e.g., 'overdue mammogram', "
        "'on warfarin — INR last drawn 8 months ago'). Narrative is "
        "truncated to 90 chars. Banners persist until removed; don't "
        "create duplicates for the same finding. Returns the generated "
        "key so the banner can be referenced/removed later."
    ),
    effect_class=AddBannerAlert,
    fields={
        "narrative": EffectField(
            type="string",
            description=(
                "Short banner text — what the clinician should see. "
                "Truncated to 90 chars. E.g. 'Overdue colonoscopy — "
                "screening interval was 10y.'"
            ),
            required=True,
        ),
        "intent": EffectField(
            type="string",
            description=(
                "Visual emphasis. 'info' for neutral context, 'warning' for "
                "issues that need attention, 'alert' for safety-critical."
            ),
            enum=_BANNER_INTENTS,
            required=True,
        ),
        "placement": EffectField(
            type="array",
            description=(
                "Where the banner appears. Most clinical alerts want "
                "['chart']; add 'timeline' to also surface on the patient "
                "timeline. Use 'profile' for identity/demographic flags."
            ),
            items={"type": "string", "enum": _BANNER_PLACEMENTS},
            min_items=1,
            max_items=len(_BANNER_PLACEMENTS),
            required=True,
        ),
        "href": EffectField(
            type="string",
            description=(
                "Optional URL the banner links to. Use for deep-links to "
                "supporting context (e.g., the lab result page)."
            ),
        ),
    },
    pre_build=lambda arguments, ctx: {
        "key": str(uuid4()),
        "narrative": arguments["narrative"].strip()[:90],
        "intent": AddBannerAlert.Intent(arguments["intent"]),
        "placement": [AddBannerAlert.Placement(p) for p in arguments["placement"]],
    },
    response_builder=lambda effect: {"ok": True, "banner_key": str(effect.key)},
    categories=("clinical_alerts",),
    returns_description=(
        "`{ok: true, banner_key: <uuid>}` — pass `banner_key` to "
        "`remove_banner_alert` later to take the banner down."
    ),
)


standard_tools.add_effect_tool(
    name="remove_banner_alert",
    description=(
        "Remove a previously-staged banner alert from the patient's chart. "
        "Takes the banner's `key` — obtained either from a prior "
        "`add_banner_alert` call (returned as `banner_key` in the response) "
        "or from `find_banner_alerts`. Use when the underlying clinical "
        "issue has been addressed (e.g., the overdue screening was "
        "completed) and the banner should no longer display."
    ),
    effect_class=RemoveBannerAlert,
    fields={
        "banner_key": EffectField(
            type="string",
            description=(
                "The banner's key — exactly as returned by add_banner_alert "
                "(``banner_key`` in the response) or find_banner_alerts "
                "(``key`` in each row)."
            ),
            required=True,
            command_field="key",
        ),
    },
    categories=("clinical_alerts",),
    returns_description="`{ok: true}`.",
)


standard_tools.add_effect_tool(
    name="create_task",
    description=(
        "Create a follow-up Task for the patient — appears in the clinician's "
        "task queue for them to act on later. Use for things the clinician "
        "should do but that can't be staged as a chart command (call patient, "
        "schedule follow-up visit, review external records). The task is not "
        "assigned to a specific user; team/assignee routing happens via the "
        "instance's task triage rules. Title is truncated to 200 chars. "
        "Returns the generated task_id so it can be referenced later."
    ),
    effect_class=AddTask,
    fields={
        "title": EffectField(
            type="string",
            description="Plain-text task title (truncated to 200 chars).",
            required=True,
        ),
    },
    pre_build=lambda arguments, ctx: {
        "id": str(uuid4()),
        "title": arguments["title"].strip()[:200],
    },
    response_builder=lambda effect: {"ok": True, "task_id": str(effect.id)},
    categories=("task_writes",),
    returns_description=(
        "`{ok: true, task_id: <uuid>}` — pass `task_id` to `update_task` "
        "or `add_task_comment` to close or annotate the task later."
    ),
)


_TASK_STATUSES = [s.value for s in TaskStatus]


standard_tools.add_effect_tool(
    name="update_task",
    description=(
        "Update an existing task — typically to close it (status=COMPLETED), "
        "reopen it (status=OPEN), or change its title/due. The task_id must "
        "come from a prior `find_tasks` or `create_task` call; this tool "
        "does not look tasks up by content. Title is truncated to 200 chars. "
        "Only the fields you supply are updated; omitted fields are left as-is."
    ),
    effect_class=UpdateTask,
    fields={
        "task_id": EffectField(
            type="string",
            description=("The task's UUID — from a prior find_tasks/create_task call."),
            required=True,
            command_field="id",
        ),
        "status": EffectField(
            type="string",
            description=(
                "New status. 'COMPLETED' marks the task done, 'CLOSED' "
                "dismisses it without completion, 'OPEN' reopens. Optional — "
                "omit to leave status unchanged."
            ),
            enum=_TASK_STATUSES,
        ),
        "title": EffectField(
            type="string",
            description="Updated task title (truncated to 200 chars). Optional.",
        ),
        "due_on": EffectField(
            type="string",
            format="date",
            description="Updated due date (ISO 8601 YYYY-MM-DD). Optional.",
            command_field="due",
        ),
    },
    inject_ctx={},
    pre_build=lambda arguments, ctx: _build_update_task_kwargs(arguments),
    categories=("task_writes",),
    returns_description="`{ok: true}`.",
)


def _build_update_task_kwargs(arguments: dict[str, Any]) -> dict[str, Any]:
    """Construct UpdateTask kwargs from model arguments.

    Handles three special-cases the lambda form can't express cleanly:
    - title truncation (only when supplied)
    - status string → TaskStatus enum coercion
    - due_on YYYY-MM-DD → datetime at midnight (UpdateTask.due is datetime)
    """
    out: dict[str, Any] = {}
    title = arguments.get("title")
    if title is not None:
        out["title"] = title.strip()[:200]
    status = arguments.get("status")
    if status is not None:
        out["status"] = TaskStatus(status)
    due_on = arguments.get("due_on")
    if due_on:
        out["due"] = datetime.fromisoformat(due_on)
    return out


standard_tools.add_effect_tool(
    name="add_task_comment",
    description=(
        "Add a comment to an existing task — use to explain *why* a task "
        "was created/closed or to add context the clinician should see when "
        "they pick up the task. The task_id must come from a prior find_tasks "
        "or create_task call."
    ),
    effect_class=AddTaskComment,
    fields={
        "task_id": EffectField(
            type="string",
            description=("The task's UUID — from a prior find_tasks/create_task call."),
            required=True,
        ),
        "body": EffectField(
            type="string",
            description="The comment text. Plain text; no markdown.",
            required=True,
        ),
    },
    inject_ctx={},
    categories=("task_writes",),
    returns_description="`{ok: true}`.",
)


_PROTOCOL_CARD_STATUSES = [s.value for s in ProtocolCard.Status]

# Command types that can be embedded inside a protocol card recommendation
# as button-triggered actions. Mirrors the originate-on-note SDK tools so the
# agent can mirror the same arg shape in the `context` field.
_RECOMMENDATION_COMMAND_TYPES = [
    cls.Meta.key
    for cls in (
        PlanCommand,
        PrescribeCommand,
        LabOrderCommand,
        ImagingOrderCommand,
        DiagnoseCommand,
        GoalCommand,
        AssessCommand,
        FollowUpCommand,
        InstructCommand,
        ReferCommand,
        StopMedicationCommand,
    )
]


def _wrap_recommendation_command(cmd: dict[str, Any]) -> dict[str, Any]:
    """Wrap an LLM-supplied ``{type, context}`` into ProtocolCard's envelope.

    Matches what :meth:`_BaseCommand.recommendation_context` produces for
    Command instances: preserves the ``{command, context}`` outer shape and
    stamps ``effect_type`` so the chart UI dispatches the right
    ``ORIGINATE_<NAME>_COMMAND`` effect when the clinician clicks the button.
    """
    cmd_type = cmd["type"]
    context = dict(cmd.get("context") or {})
    constantized = re.sub(r"(?<!^)(?=[A-Z])", "_", cmd_type).upper()
    context["effect_type"] = f"ORIGINATE_{constantized}_COMMAND"
    return {"command": {"type": cmd_type}, "context": context}


def _build_protocol_recommendation(raw: dict[str, Any]) -> Recommendation:
    """Construct a :class:`Recommendation` from an LLM-supplied dict.

    If the dict carries ``commands``, each is wrapped via
    :func:`_wrap_recommendation_command` before the Recommendation is built —
    so the LLM speaks the simple ``{type, context}`` shape while the
    serialized payload matches what home-app's ProtocolCard renderer
    expects (the same shape a hand-written
    ``Recommendation(commands=[LabOrderCommand(...)])`` would produce).
    """
    if raw.get("commands"):
        raw = {**raw, "commands": [_wrap_recommendation_command(c) for c in raw["commands"]]}
    return Recommendation(**raw)


standard_tools.add_effect_tool(
    name="add_or_update_protocol_card",
    description=(
        "Stage or update a protocol card on the patient — a clinical decision "
        "support surface with title, narrative, and a list of recommended "
        "actions the clinician can take. Pass `card_key` to update an existing "
        "card (idempotent — call again to refresh narrative/status as the "
        "underlying clinical picture changes); omit to create a new one. "
        "Status drives visual treatment: 'due' (needs action), 'satisfied' "
        "(done), 'not_applicable' (doesn't apply to this patient), 'pending' "
        "(in progress), 'not_relevant' (dismissed). Title and narrative are "
        "truncated to 200 and 500 chars respectively. Returns the card_key "
        "so the same card can be updated later."
    ),
    effect_class=ProtocolCard,
    fields={
        "title": EffectField(
            type="string",
            description=(
                "Short card title — what the clinician sees first. Truncated "
                "to 200 chars. E.g. 'Diabetes management — A1c overdue'."
            ),
            required=True,
        ),
        "narrative": EffectField(
            type="string",
            description=(
                "Body text explaining the clinical context and why this is "
                "surfacing now. Truncated to 500 chars."
            ),
            required=True,
        ),
        "status": EffectField(
            type="string",
            description="Card lifecycle status. Defaults to 'due' if omitted.",
            enum=_PROTOCOL_CARD_STATUSES,
        ),
        "card_key": EffectField(
            type="string",
            description=(
                "Stable key identifying the card. Supply the key from a prior "
                "call to update that card; omit to create a new one (a UUID "
                "is generated)."
            ),
            command_field="key",
        ),
        "recommendations": EffectField(
            type="array",
            description=(
                "Optional recommended actions surfaced beneath the card. "
                "Each is an object with `title` (required, what the action "
                "is), optional `button` (call-to-action text), optional "
                "`href` (link the button opens), and optional `commands` — "
                "a list of chart commands the button stages on the open "
                "note when clicked. When the clinician clicks the button, "
                "the platform stages each originated command as a draft "
                "for the clinician to review, edit, and commit."
            ),
            items={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "button": {"type": "string"},
                    "href": {"type": "string"},
                    "commands": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": _RECOMMENDATION_COMMAND_TYPES,
                                },
                                "context": {
                                    "type": "object",
                                    "description": (
                                        "Command-specific args. Use these "
                                        "field names exactly (they match "
                                        "the underlying Effect class) and "
                                        "the exact string values for enum "
                                        "fields. Omit fields you don't "
                                        "have a value for — the clinician "
                                        "fills them in. Per type:\n"
                                        "- plan: narrative\n"
                                        "- prescribe: fdb_code, sig, "
                                        "icd10_codes (array, max 2), "
                                        "days_supply, refills\n"
                                        "- labOrder: tests_order_codes "
                                        "(array), diagnosis_codes (array "
                                        "of ICD-10), lab_partner, comment, "
                                        "fasting_required (bool)\n"
                                        "- imagingOrder: image_code, "
                                        "diagnosis_codes (array), priority "
                                        "('Routine' | 'Urgent'), "
                                        "additional_details, comment\n"
                                        "- diagnose: icd10_code, "
                                        "today_assessment, background, "
                                        "approximate_date_of_onset "
                                        "(YYYY-MM-DD)\n"
                                        "- goal: goal_statement, priority "
                                        "('high-priority' | "
                                        "'medium-priority' | "
                                        "'low-priority'), "
                                        "achievement_status ('in-progress'"
                                        " | 'improving' | 'worsening' | "
                                        "'no-change' | 'achieved' | "
                                        "'sustaining' | 'not-achieved' | "
                                        "'no-progress'), due_date "
                                        "(YYYY-MM-DD), progress\n"
                                        "- assess: condition_id (UUID from "
                                        "find_conditions), status "
                                        "('improved' | 'stable' | "
                                        "'deteriorated'), narrative, "
                                        "background\n"
                                        "- followUp: requested_date "
                                        "(YYYY-MM-DD), comment\n"
                                        "- instruct: comment\n"
                                        "- refer: diagnosis_codes (array), "
                                        "clinical_question ('Cognitive "
                                        "Assistance (Advice/Guidance)' | "
                                        "'Assistance with Ongoing "
                                        "Management' | 'Specialized "
                                        "intervention' | 'Diagnostic "
                                        "Uncertainty'), priority "
                                        "('Routine' | 'Urgent'), "
                                        "notes_to_specialist, "
                                        "include_visit_note (bool), comment\n"
                                        "- stopMedication: medication_id "
                                        "(UUID from find_medications), "
                                        "rationale"
                                    ),
                                },
                            },
                            "required": ["type"],
                        },
                        "maxItems": 3,
                    },
                },
                "required": ["title"],
            },
            max_items=10,
        ),
        "due_in": EffectField(
            type="integer",
            description=(
                "Days from now until the card is 'due' — drives the 'Next "
                "due' text the clinician sees on the card. Use positive "
                "integers (e.g., 90 for 'recheck in 3 months'). Default "
                "-1 means no specific due date."
            ),
        ),
        "can_be_snoozed": EffectField(
            type="boolean",
            description=(
                "When true, the chart UI shows a snooze affordance on the "
                "card so the clinician can temporarily hide it without "
                "marking it satisfied. Recommended for cross-visit "
                "follow-up cards. Default false."
            ),
        ),
        "feedback_enabled": EffectField(
            type="boolean",
            description=(
                "When true, the chart UI surfaces a feedback affordance on "
                "the card — typically a dismiss / 'not relevant' control. "
                "Recommended for agent-generated cards so the clinician has "
                "a way to push back when the recommendation doesn't apply. "
                "Default false."
            ),
        ),
    },
    pre_build=lambda arguments, ctx: {
        "key": arguments.get("card_key") or str(uuid4()),
        "title": arguments["title"].strip()[:200],
        "narrative": arguments["narrative"].strip()[:500],
        "status": ProtocolCard.Status(arguments.get("status", "due")),
        "recommendations": [
            _build_protocol_recommendation(r) for r in (arguments.get("recommendations") or [])
        ],
    },
    response_builder=lambda effect: {"ok": True, "card_key": str(effect.key)},
    categories=("clinical_alerts",),
    returns_description=(
        "`{ok: true, card_key: <uuid>}` — pass `card_key` back to update "
        "the same card on a subsequent run."
    ),
)


# ---------------------------------------------------------------------------
# Originate-on-note command tools — stage drafts on the patient's current note
# ---------------------------------------------------------------------------
#
# The helper's default ``note_resolver`` reads ``ctx["note_id"]``. Triggered
# agents (ChartSummary, etc.) set this from their trigger payload; chat-style
# agents resolve the patient's current open note via
# :func:`canvas_sdk.agents.find_open_note_uuid_from_ctx` and store it on
# ctx before tool dispatch. Either way, every tool here stages a draft —
# the clinician reviews, edits, and commits in the chart UI.


_ORIGINATE_RETURNS = (
    "`{ok: true, note_id: <uuid>, command: '<command_key>', "
    "committed: false}`. Never commits — the clinician reviews the "
    "draft in the chart and decides whether to commit."
)


standard_tools.originate_command_tool(
    name="originate_plan",
    description=(
        "Stage a draft Plan command on the patient's current open note "
        "for the clinician to review, edit, and commit. NEVER commits — "
        "the clinician sees the draft in the chart and decides whether "
        "to keep it. Use when the conversation has produced a concise "
        "plan paragraph worth surfacing on the note."
    ),
    command_class=PlanCommand,
    fields={
        "narrative": EffectField(
            type="string",
            description=(
                "The plan text. Plain prose; no markdown. Keep it concise — "
                "this becomes the body of the Plan command on the note."
            ),
            required=True,
        ),
    },
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.originate_command_tool(
    name="originate_prescribe_medication",
    description=(
        "Stage a draft Prescribe command on the patient's current open note "
        "for the clinician to review, edit, and commit. NEVER commits — the "
        "clinician sees the draft in the chart and decides whether to send "
        "it. Use only when the clinician explicitly asks to prescribe."
    ),
    command_class=PrescribeCommand,
    fields={
        "fdb_code": EffectField(
            type="string",
            description=(
                "FDB code identifying the medication. If unknown, omit; "
                "the clinician will fill it in when reviewing the draft."
            ),
        ),
        "sig": EffectField(
            type="string",
            description="Patient instructions (e.g. 'Take 1 tablet by mouth daily').",
            required=True,
        ),
        "indications_icd10": EffectField(
            type="array",
            items={"type": "string"},
            max_items=2,
            description="ICD-10 codes justifying the prescription (max 2). Optional.",
            command_field="icd10_codes",
        ),
        "days_supply": EffectField(
            type="integer",
            minimum=1,
            description="Days supply for the prescription. Optional.",
        ),
        "refills": EffectField(
            type="integer",
            minimum=0,
            description="Refills (0 = no refills). Optional.",
        ),
    },
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.originate_command_tool(
    name="originate_lab_order",
    description=(
        "Stage a draft Lab Order command on the patient's current open note "
        "for the clinician to review and commit. NEVER commits. Use when the "
        "clinician asks to order labs."
    ),
    command_class=LabOrderCommand,
    fields={
        "tests_order_codes": EffectField(
            type="array",
            items={"type": "string"},
            min_items=1,
            description="Order codes for the tests to include. At least one required.",
            required=True,
        ),
        "diagnosis_codes": EffectField(
            type="array",
            items={"type": "string"},
            description="ICD-10 codes for diagnoses justifying the order.",
        ),
        "lab_partner": EffectField(
            type="string",
            description=(
                "Lab partner UUID or name. Optional; the clinician can fill it in when reviewing."
            ),
        ),
        "comment": EffectField(
            type="string",
            description="Optional free-text instructions to the lab.",
        ),
        "fasting_required": EffectField(
            type="boolean",
            description="Whether the patient needs to fast before collection.",
        ),
    },
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.originate_command_tool(
    name="originate_diagnose_condition",
    description=(
        "Stage a draft Diagnose command on the patient's current open note "
        "for the clinician to review and commit. NEVER commits. Use when the "
        "clinician wants to capture a new diagnosis."
    ),
    command_class=DiagnoseCommand,
    fields={
        "icd10_code": EffectField(
            type="string",
            description="ICD-10 code for the condition (e.g. 'E11.9').",
            required=True,
        ),
        "today_assessment": EffectField(
            type="string",
            description="Today's assessment narrative for this diagnosis.",
        ),
        "background": EffectField(
            type="string",
            description="Optional background/context for the diagnosis.",
        ),
        "approximate_date_of_onset": EffectField(
            type="string",
            format="date",
            description="ISO 8601 date of approximate onset. Optional.",
        ),
    },
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


_GOAL_PRIORITIES = [p.value for p in GoalCommand.Priority]
_GOAL_ACHIEVEMENT_STATUSES = [s.value for s in GoalCommand.AchievementStatus]


standard_tools.originate_command_tool(
    name="originate_goal",
    description=(
        "Stage a draft Goal command on the patient's current open note for "
        "the clinician to review and commit. NEVER commits. Use to capture "
        "a discrete clinical goal (e.g., 'A1c < 7.0 within 6 months', "
        "'walking 30 minutes 5x/week'). The narrative goes in goal_statement."
    ),
    command_class=GoalCommand,
    fields={
        "goal_statement": EffectField(
            type="string",
            description="Plain-text statement of the goal.",
            required=True,
        ),
        "priority": EffectField(
            type="string",
            description="Goal priority. Optional.",
            enum=_GOAL_PRIORITIES,
        ),
        "achievement_status": EffectField(
            type="string",
            description="Current achievement status. Default 'in-progress' if omitted.",
            enum=_GOAL_ACHIEVEMENT_STATUSES,
        ),
        "due_date": EffectField(
            type="string",
            format="date",
            description="ISO 8601 target date for the goal. Optional.",
        ),
        "progress": EffectField(
            type="string",
            description="Optional free-text note about current progress.",
        ),
    },
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


_ASSESS_STATUSES = [s.value for s in AssessCommand.Status]


standard_tools.originate_command_tool(
    name="originate_assessment",
    description=(
        "Stage a draft Assess command on the patient's current open note — "
        "the clinician's assessment of one of the patient's existing "
        "conditions ('how is this condition doing today'). NEVER commits. "
        "Requires the condition_id from a prior `find_conditions` call."
    ),
    command_class=AssessCommand,
    fields={
        "condition_id": EffectField(
            type="string",
            description=(
                "UUID of the condition being assessed — from a prior "
                "find_conditions call (the row's `id` field)."
            ),
            required=True,
        ),
        "status": EffectField(
            type="string",
            description="Status of the condition today relative to its prior state.",
            enum=_ASSESS_STATUSES,
        ),
        "narrative": EffectField(
            type="string",
            description="Today's assessment narrative for this condition.",
        ),
        "background": EffectField(
            type="string",
            description="Optional background/context.",
        ),
    },
    pre_build=lambda arguments, ctx: (
        {"status": AssessCommand.Status(arguments["status"])} if arguments.get("status") else {}
    ),
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.originate_command_tool(
    name="originate_follow_up",
    description=(
        "Stage a draft Follow-Up command on the patient's current open note "
        "to schedule a return visit. NEVER commits. Use when the clinician "
        "wants to plan a follow-up appointment (e.g., 'recheck in 2 weeks')."
    ),
    command_class=FollowUpCommand,
    fields={
        "requested_date": EffectField(
            type="string",
            format="date",
            description="ISO 8601 target date for the follow-up.",
        ),
        "comment": EffectField(
            type="string",
            description=(
                "Free-text reason for the follow-up (visible to scheduling). "
                "E.g., 'recheck BP after med adjustment'."
            ),
        ),
    },
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.originate_command_tool(
    name="originate_stop_medication",
    description=(
        "Stage a draft Stop-Medication command on the patient's current "
        "open note to discontinue an active medication. NEVER commits. "
        "Requires medication_id from a prior `find_medications` call. "
        "Use when the clinician decides to stop a med (side effects, "
        "ineffective, completed course)."
    ),
    command_class=StopMedicationCommand,
    fields={
        "medication_id": EffectField(
            type="string",
            description=(
                "UUID of the medication to stop — from a prior find_medications "
                "call (the row's `id` field)."
            ),
            required=True,
        ),
        "rationale": EffectField(
            type="string",
            description=(
                "Reason for stopping (e.g., 'side effects', 'completed course', "
                "'ineffective'). Visible to anyone reviewing the chart."
            ),
        ),
    },
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.add_effect_tool(
    name="originate_message",
    description=(
        "Stage a draft message from the requesting staff to this patient for "
        "the staff to review, edit, and send. NEVER sends — drafts land in "
        "the staff's outbox; the clinician hits Send. Use when the clinician "
        "explicitly asks to reply to or message the patient (e.g., 'draft a "
        "reply about her A1c', 'message the patient about their lab results'). "
        "Pull recent inbound messages via `find_messages(from_patient_only=true)` "
        "first so the draft reflects the actual conversation. Keep drafts "
        "patient-readable: plain English, short sentences, no jargon unless "
        "the clinician asked for a technical tone."
    ),
    effect_class=MessageEffect,
    effect_method="create",
    fields={
        "content": EffectField(
            type="string",
            description=(
                "The message body the patient will read. Plain text only — "
                "no markdown headings or HTML. Address the patient directly. "
                "Sign off as the staff member if appropriate; the patient "
                "sees the sender's name on the message header either way."
            ),
            required=True,
        ),
    },
    # patient_id and staff_id come from the agent's tool ctx — patient
    # from the scope_key, staff from the calling Application's session
    # (StaffSessionAuthMixin → trigger_payload["staff_id"]).
    inject_ctx={"patient_id": "recipient_id", "staff_id": "sender_id"},
    categories=("message_writes",),
    returns_description=(
        "`{ok: true, status: 'draft'}`. The draft sits unsent in the "
        "staff's outbox; the clinician reviews and decides whether to send."
    ),
)


def _originate_review_note(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Create a fresh review-category note and originate a Plan command on it.

    Drafts two effects in order: ``Note.create()`` for the note shell with
    a client-side-generated ``instance_id``, then ``PlanCommand.originate()``
    on the same ``note_uuid`` with the narrative as its body. The
    plugin-runner dispatches them in order — note row first, plan command
    second — so the originated command lands on the newly created note.

    Patient and staff identity come from the agent's ``ctx``; the agent
    supplies ``narrative`` plus the two customer-config UUIDs
    (``note_type_id`` from ``find_note_types(category='review')``,
    ``practice_location_id`` from ``find_practice_locations``). Optional
    ``title`` lets the agent name the note (e.g. "Lab review — 2026-05-15").
    ``datetime_of_service`` defaults to now if not provided.
    """
    patient_id = ctx.get("patient_id")
    staff_id = ctx.get("staff_id")
    if not patient_id:
        return {"ok": False, "error": "originate_review_note requires patient_id on ctx"}
    if not staff_id:
        return {
            "ok": False,
            "error": (
                "originate_review_note requires staff_id on ctx — the calling "
                "Application must stamp the requesting staff into trigger_payload."
            ),
        }

    narrative = (arguments.get("narrative") or "").strip()
    if not narrative:
        return {"ok": False, "error": "narrative cannot be empty"}

    note_type_id = arguments.get("note_type_id")
    practice_location_id = arguments.get("practice_location_id")
    if not note_type_id:
        return {
            "ok": False,
            "error": (
                "note_type_id is required — call find_note_types(category='review') "
                "to discover the customer's review note type UUID."
            ),
        }
    if not practice_location_id:
        return {
            "ok": False,
            "error": (
                "practice_location_id is required — call find_practice_locations "
                "to list the customer's locations and pick one (typically the "
                "staff's primary)."
            ),
        }

    title = (arguments.get("title") or "").strip() or None
    dt_arg = arguments.get("datetime_of_service")
    if dt_arg:
        try:
            dt_of_service = datetime.fromisoformat(dt_arg)
        except ValueError:
            return {
                "ok": False,
                "error": f"datetime_of_service {dt_arg!r} is not a valid ISO 8601 string",
            }
    else:
        dt_of_service = datetime.now(UTC)

    new_note_uuid = str(uuid4())

    effects: list[Any] = ctx["effects"]
    effects.append(
        NoteEffect(
            instance_id=new_note_uuid,
            patient_id=str(patient_id),
            provider_id=str(staff_id),
            practice_location_id=str(practice_location_id),
            note_type_id=str(note_type_id),
            datetime_of_service=dt_of_service,
            title=title,
        ).create()
    )
    effects.append(
        PlanCommand(
            note_uuid=new_note_uuid,
            narrative=narrative,
        ).originate()
    )
    return {
        "ok": True,
        "note_id": new_note_uuid,
        "command": "plan",
        "committed": False,
    }


standard_tools.register(
    {
        "name": "originate_review_note",
        "description": (
            "Stage a draft review-category note for the patient with a single Plan "
            "command containing the narrative. NEVER commits — the note + plan "
            "draft sit unsigned for the clinician to review, edit, and sign. Use "
            "when the clinician asks to draft a chart-review note, lab-review "
            "note, or similar narrative summary that isn't tied to a live visit. "
            "Before calling: (1) `find_note_types(category='review')` to get a "
            "`note_type_id`; (2) `find_practice_locations` to get a "
            "`practice_location_id`. Patient + requesting-staff come from the "
            "agent's scope automatically."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "narrative": {
                    "type": "string",
                    "description": (
                        "The body of the Plan command on the new note. Plain prose, "
                        "no markdown. This is what becomes the note's primary content."
                    ),
                },
                "note_type_id": {
                    "type": "string",
                    "description": (
                        "UUID of a NoteType row with category='review' — get from "
                        "`find_note_types(category='review')`. The customer's review "
                        "note type IDs vary; don't guess."
                    ),
                },
                "practice_location_id": {
                    "type": "string",
                    "description": (
                        "UUID of a PracticeLocation row — get from "
                        "`find_practice_locations`. The customer's locations vary; "
                        "don't guess."
                    ),
                },
                "title": {
                    "type": "string",
                    "description": (
                        "Optional note title (e.g., 'Lab review — 2026-05-15'). "
                        "Falls back to the NoteType's default if omitted."
                    ),
                },
                "datetime_of_service": {
                    "type": "string",
                    "format": "date-time",
                    "description": (
                        "Optional ISO 8601 datetime. Defaults to now if omitted. "
                        "Use for back-dated reviews."
                    ),
                },
            },
            "required": ["narrative", "note_type_id", "practice_location_id"],
        },
    },
    _originate_review_note,
    categories=("clinical_writes",),
    metadata={
        "command_class": PlanCommand,
        "effect_class": NoteEffect,
        "returns_description": (
            "`{ok: true, note_id: <uuid>, command: 'plan', committed: false}`. "
            "Two effects are bundled: CREATE_NOTE for the review shell and the "
            "Plan command originating onto it. Clinician reviews/edits/signs."
        ),
    },
)


__exports__ = ("standard_tools",)
