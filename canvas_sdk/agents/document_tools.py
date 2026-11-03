"""SDK-provided tools for an incoming document, registered on :data:`standard_tools`.

They act on the document a run is about, ``ctx["document_id"]``: an ``IntegrationTask``
in the data integration queue, such as a fax just received, which the platform checked
before the run started. The reads look at the document and at what it can be filed as;
the writes suggest, on the document's review form, the patient, the document type, the
report values, and the reviewer. A suggestion files nothing: a person reviews the form in
Canvas and confirms it.

The model never chooses the patient. ``match_patient`` and ``suggest_patient`` take what
the document says (name, birth date, MRN) and match it in code, suggesting a patient only
when exactly one matches, since a model choosing among near matches can file a document
to the wrong chart without noticing.
"""

from datetime import date
from typing import Any

from django.db.models import Q

from canvas_sdk.agents.standard_tools import answer_from_file, standard_tools
from canvas_sdk.effects.data_integration import (
    AssignDocumentReviewer,
    CategorizeDocument,
    LinkDocumentToPatient,
    PrefillDocumentFields,
)
from canvas_sdk.effects.data_integration.types import AnnotationItem, ReportType, TemplateType
from canvas_sdk.v1.data import (
    DocumentType,
    ImagingReportTemplate,
    IntegrationTask,
    LabReportTemplate,
    Patient,
    SpecialtyReportTemplate,
    Staff,
    Team,
)
from canvas_sdk.v1.data.integration_task import IntegrationTaskStatus

# The permission the chart's data integration queue checks.
QUEUE_PERMISSION = "api.access_dataintegration"
# The most templates one search returns; past this the model should narrow its words.
MAX_TEMPLATE_CANDIDATES = 10
# How a suggestion this tool made is labeled on the review form.
SUGGESTION_COLOR = "#2196F3"
MAX_LABEL_CHARS = 40

TEMPLATE_MODELS: dict[str, Any] = {
    "lab": LabReportTemplate,
    "imaging": ImagingReportTemplate,
    "specialty": SpecialtyReportTemplate,
}

_LABEL_PROPERTY = {
    "type": "string",
    "description": (
        f"Optional short label shown with the suggestion on the review form, up to "
        f"{MAX_LABEL_CHARS} characters, e.g. 'From fax header'."
    ),
}
_PATIENT_PROPERTIES = {
    "first_name": {"type": "string", "description": "First name as the document gives it."},
    "last_name": {"type": "string", "description": "Last name as the document gives it."},
    "birth_date": {
        "type": "string",
        "format": "date",
        "description": "Birth date as the document gives it, YYYY-MM-DD.",
    },
    "mrn": {"type": "string", "description": "The Canvas MRN, if the document shows one."},
}


def require_document_id(ctx: dict[str, Any]) -> str:
    """The run's incoming document, for a tool that only makes sense on one.

    Raises when the run is not about a document, which the agent's loop returns to the
    model as a failed tool result.
    """
    document_id: str | None = ctx.get("document_id")
    if not document_id:
        raise ValueError(
            "This run is not about an incoming document, so intake tools are unavailable"
        )
    return document_id


def _annotations(arguments: dict[str, Any]) -> list[AnnotationItem] | None:
    label = str(arguments.get("label") or "").strip()[:MAX_LABEL_CHARS]
    return [{"text": label, "color": SUGGESTION_COLOR}] if label else None


def _matching_patients(arguments: dict[str, Any]) -> tuple[list[Any], str]:
    """The patients the document's identifiers match, and what they matched on.

    An MRN counts only with the last name or birth date agreeing with it, so an MRN alone
    never names a patient. Without one, the last name and birth date are required. The
    first name, when given, must be the patient's first name or nickname. Names compare
    without case or surrounding space.
    """
    first = str(arguments.get("first_name") or "").strip()
    last = str(arguments.get("last_name") or "").strip()
    mrn = str(arguments.get("mrn") or "").strip()
    raw_birth_date = str(arguments.get("birth_date") or "").strip()
    try:
        birth_date = date.fromisoformat(raw_birth_date) if raw_birth_date else None
    except ValueError:
        raise ValueError(f"birth_date {raw_birth_date!r} is not a YYYY-MM-DD date") from None
    if mrn and not (last or birth_date):
        raise ValueError("Pass the last name or birth date with the MRN.")
    if not mrn and not (last and birth_date):
        raise ValueError("Pass the last name and birth date, with the MRN when there is one.")

    patients = Patient.objects.all()
    matched_on = []
    if mrn:
        patients = patients.filter(mrn=mrn)
        matched_on.append("mrn")
    if last:
        patients = patients.filter(last_name__iexact=last)
        matched_on.append("last_name")
    if birth_date:
        patients = patients.filter(birth_date=birth_date)
        matched_on.append("birth_date")
    if first:
        patients = patients.filter(Q(first_name__iexact=first) | Q(nickname__iexact=first))
        matched_on.append("first_name")
    found = list(patients.only("id")[:2])
    return found, ", ".join(matched_on)


def _no_match(found: list[Any]) -> dict[str, Any]:
    if not found:
        return {"match": None, "reason": "No patient matches; a person files this document."}
    return {
        "match": None,
        "reason": "More than one patient matches; a person chooses, so none is suggested.",
    }


@standard_tools.tool(
    name="read_incoming_document",
    description=(
        "Read the incoming document this run is about, such as a fax just received, and "
        "answer a question from it, with page numbers. Use it to find what the document "
        "says about who it is for (name, birth date, MRN), what kind of document it is, "
        "and the values it reports. Reads the whole file with a separate model call, so "
        "ask for everything you need in one or two questions."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "What to find in the document, in one focused question.",
            },
        },
        "required": ["question"],
    },
    categories=("intake_reads",),
    required_permissions=(QUEUE_PERMISSION,),
    returns_description=(
        "Object with `ok`, `document_id`, `title`, `channel` (e.g. fax), `answer` (with "
        "page numbers), and `note`; or `{ok: false, error}` when the file cannot be read."
    ),
    progress_label="Reading the incoming document",
)
def _read_incoming_document(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Answer a question from the run's incoming document's file."""
    document_id = require_document_id(ctx)
    gateway = ctx.get("gateway")
    if gateway is None:
        raise ValueError("read_incoming_document needs the run's gateway on ctx")
    task = (
        IntegrationTask.objects.filter(id=document_id)
        .exclude(status=IntegrationTaskStatus.JUNK)
        .only("id", "title", "channel", "document")
        .first()
    )
    if task is None:
        raise ValueError("The run's document is not in the queue.")
    answered = answer_from_file(
        task if task.document else None, str(arguments["question"]), gateway=gateway, ctx=ctx
    )
    if not answered["ok"]:
        return answered
    return {
        "document_id": document_id,
        "title": task.title or "Incoming document",
        "channel": task.channel,
        **answered,
    }


@standard_tools.tool(
    name="match_patient",
    description=(
        "Check whether the identifiers on the document match exactly one Canvas patient, "
        "without suggesting anything. Pass the last name and birth date, plus the first "
        "name and MRN when the document gives them, exactly as the document shows them. "
        "Returns the patient's id only when exactly one matches; otherwise it says none "
        "or several did and names no one. Never guess or loosen identifiers to get a "
        "match: a document no one patient matches is for a person to file."
    ),
    input_schema={"type": "object", "properties": _PATIENT_PROPERTIES},
    categories=("intake_reads",),
    required_permissions=(QUEUE_PERMISSION,),
    returns_description=(
        "`{match: {patient_id}, matched_on}` when exactly one patient matches, else "
        "`{match: null, reason}`."
    ),
    progress_label="Matching the patient",
)
def _match_patient(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """The one patient the document's identifiers match, if exactly one does."""
    require_document_id(ctx)
    found, matched_on = _matching_patients(arguments)
    if len(found) != 1:
        return _no_match(found)
    return {"match": {"patient_id": str(found[0].id)}, "matched_on": matched_on}


@standard_tools.tool(
    name="find_document_types",
    description=(
        "List the types an incoming document can be filed as, for `categorize_document`. "
        "A clinical type with a `template_type` files with a report template "
        "(`find_report_templates`) whose values `prefill_document_fields` fills in."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Optional words in the type's name, e.g. 'lab' or 'referral'.",
            },
            "report_type": {"type": "string", "enum": ["CLINICAL", "ADMINISTRATIVE"]},
        },
    },
    categories=("intake_reads",),
    required_permissions=(QUEUE_PERMISSION,),
    returns_description=(
        "Array of `{key, name, report_type, template_type}`; `template_type` is "
        "LabReportTemplate, ImagingReportTemplate, SpecialtyReportTemplate, or null."
    ),
    progress_label="Looking up document types",
)
def _find_document_types(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """The document types, narrowed by name and report type."""
    types = DocumentType.objects.order_by("name")
    if query := str(arguments.get("query") or "").strip():
        types = types.filter(name__icontains=query)
    if report_type := arguments.get("report_type"):
        types = types.filter(report_type=report_type)
    return [
        {
            "key": t.key,
            "name": t.name,
            "report_type": t.report_type,
            "template_type": t.template_type,
        }
        for t in types
    ]


@standard_tools.tool(
    name="find_report_templates",
    description=(
        "Search the report templates a lab, imaging, or specialty document is filed with, "
        "for `prefill_document_fields`. Each template lists its fields: fill in values "
        "only for these fields, keyed by the field's `code` when it has one, else its "
        "`label`. When several templates fit, choose the one whose fields match the "
        "document's values."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "template_type": {"type": "string", "enum": list(TEMPLATE_MODELS)},
            "query": {
                "type": "string",
                "description": "Words in the template's name, e.g. 'lipid' or 'CBC'.",
            },
        },
        "required": ["template_type", "query"],
    },
    categories=("intake_reads",),
    required_permissions=(QUEUE_PERMISSION,),
    returns_description=(
        "Array of up to 10 `{template_id, name, code, fields: [{code, label, units, type, "
        "required}]}`."
    ),
    progress_label="Looking up report templates",
)
def _find_report_templates(
    arguments: dict[str, Any], *, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """Active templates of one type whose name or keywords match the query."""
    model = TEMPLATE_MODELS[arguments["template_type"]]
    query = str(arguments.get("query") or "").strip()
    templates = (
        model.objects.filter(active=True)
        .filter(Q(name__icontains=query) | Q(search_keywords__icontains=query))
        .prefetch_related("fields")
        .order_by("name")[:MAX_TEMPLATE_CANDIDATES]
    )
    return [
        {
            "template_id": template.dbid,
            "name": template.name,
            "code": template.code,
            "fields": [
                {
                    "code": field.code or None,
                    "label": field.label,
                    "units": field.units,
                    "type": field.type,
                    "required": field.required,
                }
                for field in sorted(template.fields.all(), key=lambda f: f.sequence)
            ],
        }
        for template in templates
    ]


@standard_tools.tool(
    name="suggest_patient",
    description=(
        "Suggest, on the document's review form, the patient the document is for. Pass "
        "the identifiers exactly as the document shows them, as for `match_patient`: the "
        "patient is matched in code and suggested only when exactly one matches. Files "
        "nothing; a person confirms the patient."
    ),
    input_schema={
        "type": "object",
        "properties": {**_PATIENT_PROPERTIES, "label": _LABEL_PROPERTY},
    },
    categories=("intake_writes",),
    required_permissions=(QUEUE_PERMISSION,),
    effect_types=("LINK_DOCUMENT_TO_PATIENT",),
    returns_description=(
        "`{ok: true, patient_id, matched_on}` when one patient matched and was suggested, "
        "else `{ok: false, reason}`."
    ),
    progress_label="Suggesting the patient",
)
def _suggest_patient(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Suggest the one patient the document's identifiers match."""
    document_id = require_document_id(ctx)
    found, matched_on = _matching_patients(arguments)
    if len(found) != 1:
        return {"ok": False, **_no_match(found)}
    patient = found[0]
    ctx["effects"].append(
        LinkDocumentToPatient(
            document_id=document_id,
            patient_key=str(patient.id),
            annotations=_annotations(arguments),
        ).apply()
    )
    return {"ok": True, "patient_id": str(patient.id), "matched_on": matched_on}


@standard_tools.tool(
    name="categorize_document",
    description=(
        "Suggest, on the document's review form, the type of document it is. "
        "`document_type_key` is a `key` from `find_document_types`. Files nothing; a "
        "person confirms the type."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "document_type_key": {"type": "string", "description": "From find_document_types."},
            "label": _LABEL_PROPERTY,
        },
        "required": ["document_type_key"],
    },
    categories=("intake_writes",),
    required_permissions=(QUEUE_PERMISSION,),
    effect_types=("CATEGORIZE_DOCUMENT",),
    returns_description="`{ok: true, document_type: {key, name, template_type}}`.",
    progress_label="Suggesting the document type",
)
def _categorize_document(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Suggest a document type from the instance's types."""
    document_id = require_document_id(ctx)
    key = str(arguments["document_type_key"])
    document_type = DocumentType.objects.filter(key=key).first()
    if document_type is None:
        raise ValueError(f"No document type with key {key!r}; use find_document_types.")
    ctx["effects"].append(
        CategorizeDocument(
            document_id=document_id,
            document_type={
                "key": document_type.key,
                "name": document_type.name,
                "report_type": ReportType(document_type.report_type),
                "template_type": (
                    TemplateType(document_type.template_type)
                    if document_type.template_type
                    else None
                ),
            },
            annotations=_annotations(arguments),
        ).apply()
    )
    return {
        "ok": True,
        "document_type": {
            "key": document_type.key,
            "name": document_type.name,
            "template_type": document_type.template_type,
        },
    }


@standard_tools.tool(
    name="prefill_document_fields",
    description=(
        "Fill in, on the document's review form, the values a lab, imaging, or specialty "
        "report gives, for a template from `find_report_templates`. `fields` maps each "
        "template field's `code` (or `label`, when it has no code) to the value exactly "
        "as the document reports it. Leave out a value the document does not give; never "
        "estimate one. Files nothing; a person confirms the values."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "template_type": {"type": "string", "enum": list(TEMPLATE_MODELS)},
            "template_id": {"type": "integer", "description": "From find_report_templates."},
            "fields": {
                "type": "object",
                "description": (
                    "Field code or label -> {value, unit?, reference_range?, abnormal?}."
                ),
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "unit": {"type": "string"},
                        "reference_range": {"type": "string"},
                        "abnormal": {"type": "boolean"},
                    },
                    "required": ["value"],
                },
            },
            "label": _LABEL_PROPERTY,
        },
        "required": ["template_type", "template_id", "fields"],
    },
    categories=("intake_writes",),
    required_permissions=(QUEUE_PERMISSION,),
    effect_types=("UPDATE_DOCUMENT_FIELDS",),
    returns_description="`{ok: true, template_id, template_name, filled: [<field>]}`.",
    progress_label="Filling in report values",
)
def _prefill_document_fields(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Prefill a template's fields, refusing any field the template does not have."""
    document_id = require_document_id(ctx)
    model = TEMPLATE_MODELS[arguments["template_type"]]
    template_id = int(arguments["template_id"])
    template = (
        model.objects.filter(dbid=template_id, active=True).prefetch_related("fields").first()
    )
    if template is None:
        raise ValueError(
            f"No active {arguments['template_type']} template {template_id}; use "
            "find_report_templates."
        )
    keys = {field.code or field.label for field in template.fields.all()}
    by_label = {
        field.label.casefold(): field.code or field.label for field in template.fields.all()
    }
    values = arguments.get("fields")
    if not isinstance(values, dict) or not values:
        raise ValueError("Pass `fields` with at least one value.")
    filled: dict[str, Any] = {}
    unknown = []
    for name, data in values.items():
        key = name if name in keys else by_label.get(str(name).casefold())
        if key is None:
            unknown.append(str(name))
            continue
        if not isinstance(data, dict) or not str(data.get("value") or "").strip():
            raise ValueError(f"Pass a value for {name}.")
        entry: dict[str, Any] = {"value": str(data["value"]).strip()}
        for optional in ("unit", "reference_range"):
            if data.get(optional):
                entry[optional] = str(data[optional]).strip()
        if isinstance(data.get("abnormal"), bool):
            entry["abnormal"] = data["abnormal"]
        filled[key] = entry
    if unknown:
        raise ValueError(
            f"{template.name} has no field {', '.join(unknown)}; use the field codes or "
            "labels find_report_templates lists."
        )
    ctx["effects"].append(
        PrefillDocumentFields(
            document_id=document_id,
            templates=[
                {"template_id": template.dbid, "template_name": template.name, "fields": filled}
            ],
            annotations=_annotations(arguments),
        ).apply()
    )
    return {
        "ok": True,
        "template_id": template.dbid,
        "template_name": template.name,
        "filled": sorted(filled),
    }


@standard_tools.tool(
    name="assign_document_reviewer",
    description=(
        "Suggest who reviews the document: a staff member, a team, or both. The review "
        "stays required; a person confirms the assignment."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "staff_id": {"type": "string", "description": "The reviewer's staff id."},
            "team_id": {"type": "string", "description": "The reviewing team's id."},
            "label": _LABEL_PROPERTY,
        },
    },
    categories=("intake_writes",),
    required_permissions=(QUEUE_PERMISSION,),
    effect_types=("ASSIGN_DOCUMENT_REVIEWER",),
    returns_description="`{ok: true, staff_id, team_id}`.",
    progress_label="Suggesting the reviewer",
)
def _assign_document_reviewer(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Suggest an active staff reviewer and/or a team, with review still required."""
    document_id = require_document_id(ctx)
    staff_id = str(arguments.get("staff_id") or "").strip() or None
    team_id = str(arguments.get("team_id") or "").strip() or None
    if not staff_id and not team_id:
        raise ValueError("Pass staff_id, team_id, or both.")
    if staff_id and not Staff.objects.filter(id=staff_id, active=True).exists():
        raise ValueError(f"No active staff member {staff_id!r}.")
    if team_id and not Team.objects.filter(id=team_id).exists():
        raise ValueError(f"No team {team_id!r}.")
    ctx["effects"].append(
        AssignDocumentReviewer(
            document_id=document_id,
            reviewer_id=staff_id,
            team_id=team_id,
            annotations=_annotations(arguments),
        ).apply()
    )
    return {"ok": True, "staff_id": staff_id, "team_id": team_id}


__exports__ = ()
