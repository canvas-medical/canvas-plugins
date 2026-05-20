"""Tools exposed to the ChartChatAgent.

Two layers:

1. **SDK-provided** :data:`canvas_sdk.agents.standard_tools` — clinical
   reads (demographics, conditions, medications, lab results, assessments)
   with patient-scope enforcement baked in.
2. **Plugin-defined** below:
   - Legacy thin reads (``list_active_conditions``, ``recent_lab_results``)
     kept for backwards compatibility; the SDK's ``find_conditions`` /
     ``find_lab_results`` are the more flexible newer surface.
   - Effect tools that stage clinician-reviewable actions:
     ``create_task`` (emits :class:`AddTask`), and three originate-only
     command tools (``originate_prescribe_medication``,
     ``originate_lab_order``, ``originate_diagnose_condition``) that drop
     a draft command onto the patient's current open note. None of them
     commit — the clinician reviews/edits/commits in the chart UI.

The originate tools need a note to land on; ``_find_open_note`` picks
the patient's most-recent note in a mutable state (NEW, UNLOCKED,
CONVERTED). If no such note exists the tool fails with a structured
error so the model can tell the clinician.
"""

from typing import Any
from uuid import uuid4

from canvas_sdk.agents import ToolRegistry, standard_tools
from canvas_sdk.commands import DiagnoseCommand, LabOrderCommand, PrescribeCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.task.task import AddTask
from canvas_sdk.v1.data import Condition, LabValue, Note
from canvas_sdk.v1.data.note import NoteStates

# Note states the chart-chat originate tools accept as the landing note for
# a draft command. Locked/signed/deleted/etc. notes are immutable.
_OPEN_NOTE_STATES = (
    NoteStates.NEW,
    NoteStates.UNLOCKED,
    NoteStates.CONVERTED,
)


def _find_open_note(patient_id: str) -> Note | None:
    """Return the patient's most-recent mutable note, or None if none exists."""
    return (
        Note.objects.filter(
            patient__id=patient_id,
            current_state__state__in=_OPEN_NOTE_STATES,
        )
        .order_by("-datetime_of_service")
        .first()
    )


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


# ---------------------------------------------------------------------------
# Effect tools — stage clinician-reviewable actions
# ---------------------------------------------------------------------------


@tools.tool(
    name="create_task",
    description=(
        "Create a follow-up Task for the patient — appears in the clinician's "
        "task queue for them to act on later. Use for things the clinician "
        "should do but that can't be staged as a chart command (call patient, "
        "schedule follow-up visit, review external records). Do NOT use this "
        "as a substitute for the originate tools — if there's a draft "
        "prescription/lab/diagnosis to stage, use those instead."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Plain-text task title (truncated to 200 chars).",
            },
        },
        "required": ["title"],
    },
)
def _create_task(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage an AddTask effect; returns the client-generated task UUID."""
    effects: list[Effect] = ctx["effects"]
    patient_id: str = ctx["patient_id"]
    title: str = arguments["title"].strip()[:200]
    task_id = str(uuid4())
    effects.append(AddTask(id=task_id, patient_id=patient_id, title=title).apply())
    return {"ok": True, "task_id": task_id}


@tools.tool(
    name="originate_prescribe_medication",
    description=(
        "Stage a draft Prescribe command on the patient's current open note "
        "for the clinician to review, edit, and commit. NEVER commits — the "
        "clinician sees the draft in the chart and decides whether to send "
        "it. Use only when the clinician explicitly asks to prescribe."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "fdb_code": {
                "type": "string",
                "description": (
                    "FDB code identifying the medication. If unknown, omit; "
                    "the clinician will fill it in when reviewing the draft."
                ),
            },
            "sig": {
                "type": "string",
                "description": "Patient instructions (e.g. 'Take 1 tablet by mouth daily').",
            },
            "indications_icd10": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 2,
                "description": ("ICD-10 codes justifying the prescription (max 2). Optional."),
            },
            "days_supply": {
                "type": "integer",
                "minimum": 1,
                "description": "Days supply for the prescription. Optional.",
            },
            "refills": {
                "type": "integer",
                "minimum": 0,
                "description": "Refills (0 = no refills). Optional.",
            },
        },
        "required": ["sig"],
    },
)
def _originate_prescribe_medication(
    arguments: dict[str, Any], *, ctx: dict[str, Any]
) -> dict[str, Any]:
    """Stage PrescribeCommand.originate() onto the patient's current open note."""
    note = _find_open_note(ctx["patient_id"])
    if note is None:
        return {
            "ok": False,
            "error": (
                "No open note for this patient — ask the clinician to open or "
                "create a note before requesting prescription drafts."
            ),
        }
    effects: list[Effect] = ctx["effects"]
    command = PrescribeCommand(
        note_uuid=str(note.id),
        fdb_code=arguments.get("fdb_code"),
        sig=arguments["sig"],
        icd10_codes=list(arguments.get("indications_icd10") or []),
        days_supply=arguments.get("days_supply"),
        refills=arguments.get("refills"),
    )
    effects.append(command.originate())
    return {"ok": True, "note_id": str(note.id), "command": "prescribe", "committed": False}


@tools.tool(
    name="originate_lab_order",
    description=(
        "Stage a draft Lab Order command on the patient's current open note "
        "for the clinician to review and commit. NEVER commits. Use when the "
        "clinician asks to order labs."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "tests_order_codes": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": ("Order codes for the tests to include. At least one required."),
            },
            "diagnosis_codes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "ICD-10 codes for diagnoses justifying the order.",
            },
            "lab_partner": {
                "type": "string",
                "description": (
                    "Lab partner UUID or name. Optional; the clinician can "
                    "fill it in when reviewing."
                ),
            },
            "comment": {
                "type": "string",
                "description": "Optional free-text instructions to the lab.",
            },
            "fasting_required": {
                "type": "boolean",
                "description": "Whether the patient needs to fast before collection.",
            },
        },
        "required": ["tests_order_codes"],
    },
)
def _originate_lab_order(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage LabOrderCommand.originate() onto the patient's current open note."""
    note = _find_open_note(ctx["patient_id"])
    if note is None:
        return {
            "ok": False,
            "error": (
                "No open note for this patient — ask the clinician to open or "
                "create a note before requesting lab-order drafts."
            ),
        }
    effects: list[Effect] = ctx["effects"]
    command = LabOrderCommand(
        note_uuid=str(note.id),
        tests_order_codes=list(arguments["tests_order_codes"]),
        diagnosis_codes=list(arguments.get("diagnosis_codes") or []),
        lab_partner=arguments.get("lab_partner"),
        comment=arguments.get("comment"),
        fasting_required=bool(arguments.get("fasting_required", False)),
    )
    effects.append(command.originate())
    return {"ok": True, "note_id": str(note.id), "command": "lab_order", "committed": False}


@tools.tool(
    name="originate_diagnose_condition",
    description=(
        "Stage a draft Diagnose command on the patient's current open note "
        "for the clinician to review and commit. NEVER commits. Use when the "
        "clinician wants to capture a new diagnosis."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "icd10_code": {
                "type": "string",
                "description": "ICD-10 code for the condition (e.g. 'E11.9').",
            },
            "today_assessment": {
                "type": "string",
                "description": "Today's assessment narrative for this diagnosis.",
            },
            "background": {
                "type": "string",
                "description": "Optional background/context for the diagnosis.",
            },
            "approximate_date_of_onset": {
                "type": "string",
                "format": "date",
                "description": "ISO 8601 date of approximate onset. Optional.",
            },
        },
        "required": ["icd10_code"],
    },
)
def _originate_diagnose_condition(
    arguments: dict[str, Any], *, ctx: dict[str, Any]
) -> dict[str, Any]:
    """Stage DiagnoseCommand.originate() onto the patient's current open note."""
    note = _find_open_note(ctx["patient_id"])
    if note is None:
        return {
            "ok": False,
            "error": (
                "No open note for this patient — ask the clinician to open or "
                "create a note before requesting a diagnosis draft."
            ),
        }
    effects: list[Effect] = ctx["effects"]
    command = DiagnoseCommand(
        note_uuid=str(note.id),
        icd10_code=arguments["icd10_code"],
        today_assessment=arguments.get("today_assessment"),
        background=arguments.get("background"),
        approximate_date_of_onset=arguments.get("approximate_date_of_onset"),
    )
    effects.append(command.originate())
    return {"ok": True, "note_id": str(note.id), "command": "diagnose", "committed": False}
