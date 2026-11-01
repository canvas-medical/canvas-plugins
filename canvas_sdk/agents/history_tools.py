"""SDK-provided tools for recording a patient's history, registered on :data:`standard_tools`.

``find_clinical_codes`` looks up the codes these commands need (ICD-10, FDB, allergen
concepts, SNOMED, CVX and CPT) from Canvas's ontology services, the same searches the
chart's own pickers make. The ``originate_*`` tools stage a draft of each history
command on the patient's open note, never committing it, and refuse what would be wrong
to stage: a duplicate of what the chart already records, history text that would not
resolve to the condition meant, or a controlled substance.
"""

from datetime import date
from typing import Any
from urllib.parse import quote

from canvas_sdk.agents.standard_tools import (
    _ORIGINATE_RETURNS,
    _patients_record_check,
    standard_tools,
)
from canvas_sdk.agents.tool_registry import EffectField, require_patient_id
from canvas_sdk.commands import (
    AllergyCommand,
    FamilyHistoryCommand,
    ImmunizationStatementCommand,
    MedicalHistoryCommand,
    MedicationStatementCommand,
    PastSurgicalHistoryCommand,
    RemoveAllergyCommand,
    ResolveConditionCommand,
    VitalsCommand,
)
from canvas_sdk.commands.commands.allergy import Allergen, AllergenType
from canvas_sdk.commands.constants import CodeSystems, Coding
from canvas_sdk.utils.http import ontologies_http, science_http
from canvas_sdk.v1.data import AllergyIntolerance, Condition, Medication
from logger import log

# The most candidates one search returns; past this the model should narrow its words.
MAX_CODE_CANDIDATES = 10
# FDB's code for an obsolete medication, which resolves to nothing when staged.
OBSOLETE_FDB_STATUS = "3"
# FDB's DEA schedule codes: "1" to "5" are schedules I to V, "0" unscheduled.
DEA_SCHEDULED = frozenset({"1", "2", "3", "4", "5"})
DEA_UNSCHEDULED = "0"


class CodeSearchUnavailable(RuntimeError):
    """An ontology service did not answer; the model is told to try again."""


def _get(client: Any, path: str) -> Any:
    """The JSON body of a GET on an ontology service, raising when it did not answer."""
    try:
        response = client.get_json(path)
    except Exception as exc:
        log.warning(f"history_tools lookup failed: {type(exc).__name__}")
        raise CodeSearchUnavailable("The code search did not answer; try again.") from exc
    if response.status_code != 200:
        raise CodeSearchUnavailable(f"The code search answered {response.status_code}; try again.")
    return response.json()


def _items(body: Any) -> list[dict[str, Any]]:
    """The rows of a paginated (``{"results": [...]}``) or bare-list response."""
    rows = body.get("results") if isinstance(body, dict) else body
    return [row for row in rows or [] if isinstance(row, dict)]


def _condition_rows(query: str) -> list[dict[str, Any]]:
    body = _get(science_http, f"/search/condition/?query={quote(query, safe='')}")
    return [
        {
            "icd10_code": str(row.get("icd10_code") or ""),
            "display": str(row.get("icd10_text") or row.get("preferred_snomed_term") or ""),
            "snomed_code": str(row.get("snomed_concept_id") or ""),
        }
        for row in _items(body)
        if row.get("icd10_code")
    ]


def _medical_history_rows(query: str) -> list[dict[str, Any]]:
    """The past-medical-history list the chart's picker and the stored entry come from."""
    body = _get(
        science_http,
        f"/search/medical-history-condition/?query={quote(query, safe='')}"
        f"&date={date.today():%Y-%m-%d}&limit=100",
    )
    return [
        {"icd10_code": str(row["icd10_code"]), "display": str(row["icd10_text"])}
        for row in _items(body)
        if row.get("icd10_code") and row.get("icd10_text")
    ]


def _medication_rows(query: str) -> list[dict[str, Any]]:
    body = _get(science_http, f"/search/grouped-medication/?query={quote(query, safe='')}&limit=50")
    return [
        {
            "fdb_code": str(row["med_medication_id"]),
            "display": str(
                row.get("med_medication_description") or row.get("description_and_quantity") or ""
            ),
            "rxnorm_rxcui": str(row.get("rxnorm_rxcui") or ""),
        }
        for row in _items(body)
        if row.get("med_medication_id")
        and str(row.get("med_medication_status_code", "0")) != OBSOLETE_FDB_STATUS
    ]


def _allergen_rows(query: str) -> list[dict[str, Any]]:
    """The allergen picklist the chart's Allergy command searches."""
    body = _get(
        ontologies_http,
        f"/fdb/allergy/?dam_allergen_concept_id_description__fts={quote(query, safe='')}",
    )
    return [
        {
            "concept_id": int(row["dam_allergen_concept_id"]),
            "concept_type": int(row.get("dam_allergen_concept_id_type") or 0),
            "display": str(row.get("dam_allergen_concept_id_description") or ""),
        }
        for row in _items(body)
        if row.get("dam_allergen_concept_id")
        and int(row.get("dam_allergen_concept_id_type") or 0) in {t.value for t in AllergenType}
    ]


def _snomed_rows(path: str) -> list[dict[str, Any]]:
    return [
        {
            "snomed_code": str(row["concept_id"]),
            "display": str(row.get("term") or row.get("display") or ""),
        }
        for row in _items(_get(science_http, path))
        if row.get("concept_id")
    ]


def _family_history_rows(query: str) -> list[dict[str, Any]]:
    return _snomed_rows(f"/search/family-history/?query={quote(query, safe='')}")


def _surgical_history_rows(query: str) -> list[dict[str, Any]]:
    return _snomed_rows(
        f"/search/surgical-history-procedure/?query={quote(query, safe='')}&limit=100"
    )


def _immunization_rows(query: str) -> list[dict[str, Any]]:
    """Vaccines as the chart's Immunize picker lists them, each with its CVX and CPT."""
    body = _get(ontologies_http, f"/cpt/immunization/?name_or_code={quote(query, safe='')}")
    return [
        {
            "cvx_code": str(row["cvx_code"]),
            "cpt_code": str(row["cpt_code"]),
            "display": str(row.get("long_name") or row.get("medium_name") or ""),
        }
        for row in _items(body)
        if row.get("cvx_code") and row.get("cpt_code")
    ]


CODE_SEARCHES = {
    "condition": _condition_rows,
    "medical_history": _medical_history_rows,
    "medication": _medication_rows,
    "allergen": _allergen_rows,
    "family_history": _family_history_rows,
    "surgical_history": _surgical_history_rows,
    "immunization": _immunization_rows,
}


@standard_tools.tool(
    name="find_clinical_codes",
    description=(
        "Look up the codes a history command needs, by name, from Canvas's own "
        "vocabularies, as the chart's pickers do. `kind` is what to look up: "
        "`medical_history` (past conditions, for `originate_medical_history`), "
        "`condition` (ICD-10 diagnoses), `medication` (FDB, for "
        "`originate_medication_statement`), `allergen` (for `originate_allergy`), "
        "`family_history` and `surgical_history` (SNOMED, for the history tools), or "
        "`immunization` (CVX and CPT, for `originate_immunization_statement`). Use the "
        "codes it returns exactly; never write a code from memory. When several "
        "candidates fit, ask the clinician which one they mean."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "kind": {"type": "string", "enum": list(CODE_SEARCHES)},
            "query": {
                "type": "string",
                "description": "The name to search for, e.g. 'penicillin' or 'appendectomy'.",
            },
        },
        "required": ["kind", "query"],
    },
    categories=("config_reads",),
    returns_description=(
        "Array of up to 10 candidates, each with `display` and its codes: `icd10_code` "
        "(condition, medical_history), `snomed_code` (condition, family_history, "
        "surgical_history), `fdb_code` and `rxnorm_rxcui` (medication), `concept_id` and "
        "`concept_type` (allergen), or `cvx_code` and `cpt_code` (immunization)."
    ),
    progress_label="Looking up codes",
)
def _find_clinical_codes(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Candidate codes for a name, from the ontology service the kind lives in."""
    query = str(arguments.get("query") or "").strip()
    if not query:
        raise ValueError("query is required")
    return CODE_SEARCHES[arguments["kind"]](query)[:MAX_CODE_CANDIDATES]


def _history_text_for(icd10_code: str, display: str) -> str:
    """The past-medical-history text the chart stores as ``icd10_code``.

    Canvas searches the text a Medical History command carries and keeps the first
    match, so the text sent must be one whose first match is this code. Refuses rather
    than stage an entry for the wrong condition, or an empty one.
    """
    wanted = icd10_code.replace(".", "").upper()

    def first_code(text: str) -> str:
        rows = _medical_history_rows(text)
        return rows[0]["icd10_code"].replace(".", "").upper() if rows else ""

    candidates = [display] if display else []
    candidates += [
        row["display"]
        for row in _medical_history_rows(icd10_code)
        if row["icd10_code"].replace(".", "").upper() == wanted
    ]
    for text in candidates:
        if text and first_code(text) == wanted:
            return text
    raise ValueError(
        f"No past-medical-history entry resolves to {icd10_code}. Look it up with "
        "find_clinical_codes (kind 'medical_history') and pass a code and display "
        "from its results."
    )


def _medical_history_pre_build(arguments: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    text = _history_text_for(str(arguments["icd10_code"]), str(arguments.get("display") or ""))
    return {"past_medical_history": text}


standard_tools.originate_command_tool(
    name="originate_medical_history",
    description=(
        "Stage a draft Medical History command recording a past or ongoing condition "
        "on the patient's open note. NEVER commits. Look the condition up first with "
        "`find_clinical_codes` (kind 'medical_history') and pass its `icd10_code` and "
        "`display`; the tool refuses a code whose entry would not resolve."
    ),
    command_class=MedicalHistoryCommand,
    fields={
        "icd10_code": EffectField(
            type="string",
            description="ICD-10 code from find_clinical_codes (kind 'medical_history').",
            required=True,
            pre_build_only=True,
        ),
        "display": EffectField(
            type="string",
            description="The `display` that came with the code.",
            pre_build_only=True,
        ),
        "approximate_start_date": EffectField(
            type="string",
            format="date",
            description="ISO 8601 date it began, if known.",
            editable=True,
        ),
        "approximate_end_date": EffectField(
            type="string",
            format="date",
            description="ISO 8601 date it ended, if it has.",
            editable=True,
        ),
        "show_on_condition_list": EffectField(
            type="boolean",
            description="Whether it appears on the conditions list. Defaults to true.",
            editable=True,
        ),
        "comments": EffectField(
            type="string", description="Optional comment, up to 1000 chars.", editable=True
        ),
    },
    pre_build=_medical_history_pre_build,
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


def _dea_schedule(fdb_code: str) -> str | None:
    """FDB's DEA schedule for a medication: "1" to "5", "" when unscheduled, None unknown.

    FDB keeps the schedule on a medication's representative NDC, so this reads the
    medication and then the NDC, the same two reads the chart makes.
    """
    try:
        medication = _get(ontologies_http, f"/fdb/grouped-medication/{quote(fdb_code, safe='')}/")
        ndc = next(
            (
                str(quantity["representative_ndc"])
                for quantity in (medication or {}).get("clinical_quantities") or []
                if quantity.get("representative_ndc")
            ),
            "",
        )
        if not ndc:
            return None
        code = str(
            (_get(ontologies_http, f"/fdb/ndc/{quote(ndc, safe='')}/") or {}).get(
                "drug_enforcement_administration_code"
            )
            or ""
        )
    except CodeSearchUnavailable:
        return None
    if code == DEA_UNSCHEDULED:
        return ""
    return code if code in DEA_SCHEDULED else None


def _medication_statement_pre_build(
    arguments: dict[str, Any], ctx: dict[str, Any]
) -> dict[str, Any]:
    """A coded medication the patient is not already recorded as taking, and not controlled."""
    fdb_code = str(arguments["fdb_code"])
    if (
        Medication.objects.active()
        .filter(
            patient__id=require_patient_id(ctx),
            codings__system=CodeSystems.FDB,
            codings__code=fdb_code,
        )
        .exists()
    ):
        raise ValueError("The patient's medication list already has this medication.")
    schedule = _dea_schedule(fdb_code)
    if schedule is None:
        raise ValueError(
            "Could not confirm this medication is not a controlled substance; the "
            "clinician should add it in the note themselves."
        )
    if schedule:
        raise ValueError(
            f"This is a Schedule {schedule} controlled substance; the clinician should "
            "add it in the note themselves."
        )
    # A coded entry keeps drug-interaction checking on, which a free-text one turns off.
    return {
        "fdb_code": Coding(
            system=CodeSystems.FDB, code=fdb_code, display=str(arguments.get("display") or "")
        )
    }


standard_tools.originate_command_tool(
    name="originate_medication_statement",
    description=(
        "Stage a draft Medication Statement recording a medication the patient takes "
        "(prescribed elsewhere, or over the counter) on the patient's open note. NEVER "
        "commits, and never prescribes. Look the medication up with "
        "`find_clinical_codes` (kind 'medication') and pass its `fdb_code` and "
        "`display`. Refuses a medication already on the list, and a controlled "
        "substance, which the clinician records themselves."
    ),
    command_class=MedicationStatementCommand,
    fields={
        "fdb_code": EffectField(
            type="string",
            description="FDB code from find_clinical_codes (kind 'medication').",
            required=True,
            pre_build_only=True,
        ),
        "display": EffectField(
            type="string",
            description="The `display` that came with the code.",
            pre_build_only=True,
        ),
        "sig": EffectField(
            type="string",
            description="How the patient takes it, e.g. '1 tablet daily'.",
            editable=True,
        ),
    },
    pre_build=_medication_statement_pre_build,
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


_SEVERITIES = [severity.value for severity in AllergyCommand.Severity]


def _allergy_pre_build(arguments: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """An allergen the patient's allergy list does not already have."""
    concept_id = int(arguments["concept_id"])
    # The chart records an allergen as an FDB coding whose code is its concept id.
    if (
        AllergyIntolerance.objects.committed()
        .filter(
            patient__id=require_patient_id(ctx),
            deleted=False,
            status="active",
            codings__system=CodeSystems.FDB,
            codings__code=str(concept_id),
        )
        .exists()
    ):
        raise ValueError("The patient's allergy list already has this allergen.")
    return {
        "allergy": Allergen(
            concept_id=concept_id, concept_type=AllergenType(int(arguments["concept_type"]))
        )
    }


standard_tools.originate_command_tool(
    name="originate_allergy",
    description=(
        "Stage a draft Allergy command on the patient's open note. NEVER commits. Look "
        "the allergen up with `find_clinical_codes` (kind 'allergen') and pass its "
        "`concept_id` and `concept_type`. Refuses an allergen already on the list."
    ),
    command_class=AllergyCommand,
    fields={
        "concept_id": EffectField(
            type="integer",
            description="Allergen concept id from find_clinical_codes (kind 'allergen').",
            required=True,
            pre_build_only=True,
        ),
        "concept_type": EffectField(
            type="integer",
            description="The `concept_type` that came with it.",
            required=True,
            pre_build_only=True,
        ),
        "severity": EffectField(
            type="string",
            enum=_SEVERITIES,
            description="Severity, if known.",
            editable=True,
        ),
        "narrative": EffectField(
            type="string", description="The reaction, in words, up to 512 chars.", editable=True
        ),
        "approximate_date": EffectField(
            type="string",
            format="date",
            description="ISO 8601 date of onset, if known.",
            editable=True,
        ),
    },
    pre_build=_allergy_pre_build,
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


def _snomed_coding(argument: str, command_field: str) -> Any:
    """A ``pre_build`` that sends the model's SNOMED code as a named Coding."""

    def pre_build(arguments: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        return {
            command_field: Coding(
                system=CodeSystems.SNOMED,
                code=str(arguments[argument]),
                display=str(arguments.get("display") or ""),
            )
        }

    return pre_build


standard_tools.originate_command_tool(
    name="originate_family_history",
    description=(
        "Stage a draft Family History command on the patient's open note. NEVER "
        "commits. Look the condition up with `find_clinical_codes` (kind "
        "'family_history') and pass its `snomed_code` and `display`, with the relative."
    ),
    command_class=FamilyHistoryCommand,
    fields={
        "snomed_code": EffectField(
            type="string",
            description="SNOMED code from find_clinical_codes (kind 'family_history').",
            required=True,
            pre_build_only=True,
        ),
        "display": EffectField(
            type="string", description="The `display` that came with it.", pre_build_only=True
        ),
        "relative": EffectField(
            type="string", description="The relative, e.g. 'mother'.", required=True, editable=True
        ),
        "note": EffectField(
            type="string", description="Optional note, up to 512 chars.", editable=True
        ),
    },
    pre_build=_snomed_coding("snomed_code", "family_history"),
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.originate_command_tool(
    name="originate_surgical_history",
    description=(
        "Stage a draft Past Surgical History command on the patient's open note. NEVER "
        "commits. Look the procedure up with `find_clinical_codes` (kind "
        "'surgical_history') and pass its `snomed_code` and `display`."
    ),
    command_class=PastSurgicalHistoryCommand,
    fields={
        "snomed_code": EffectField(
            type="string",
            description="SNOMED code from find_clinical_codes (kind 'surgical_history').",
            required=True,
            pre_build_only=True,
        ),
        "display": EffectField(
            type="string", description="The `display` that came with it.", pre_build_only=True
        ),
        "approximate_date": EffectField(
            type="string",
            format="date",
            description="ISO 8601 date of the surgery, if known.",
            editable=True,
        ),
        "comment": EffectField(
            type="string", description="Optional comment, up to 1000 chars.", editable=True
        ),
    },
    pre_build=_snomed_coding("snomed_code", "past_surgical_history"),
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


def _immunization_pre_build(arguments: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    display = str(arguments.get("display") or "")
    return {
        "cvx_code": Coding(
            system=CodeSystems.CVX, code=str(arguments["cvx_code"]), display=display
        ),
        "cpt_code": Coding(
            system=CodeSystems.CPT, code=str(arguments["cpt_code"]), display=display
        ),
    }


standard_tools.originate_command_tool(
    name="originate_immunization_statement",
    description=(
        "Stage a draft Immunization Statement recording a vaccine given elsewhere on the "
        "patient's open note. NEVER commits. Look the vaccine up with "
        "`find_clinical_codes` (kind 'immunization') and pass its `cvx_code`, `cpt_code`, "
        "and `display`."
    ),
    command_class=ImmunizationStatementCommand,
    fields={
        "cvx_code": EffectField(
            type="string",
            description="CVX code from find_clinical_codes (kind 'immunization').",
            required=True,
            pre_build_only=True,
        ),
        "cpt_code": EffectField(
            type="string",
            description="The `cpt_code` that came with it.",
            required=True,
            pre_build_only=True,
        ),
        "display": EffectField(
            type="string", description="The `display` that came with it.", pre_build_only=True
        ),
        "approximate_date": EffectField(
            type="string",
            format="date",
            description="ISO 8601 date it was given, if known.",
            editable=True,
        ),
        "comments": EffectField(
            type="string", description="Optional comment, up to 255 chars.", editable=True
        ),
    },
    pre_build=_immunization_pre_build,
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


_READINGS = (
    "height",
    "weight_lbs",
    "body_temperature",
    "blood_pressure_systole",
    "blood_pressure_diastole",
    "pulse",
    "respiration_rate",
    "oxygen_saturation",
)


def _require_a_reading(arguments: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not any(arguments.get(reading) is not None for reading in _READINGS):
        raise ValueError("Pass at least one reading.")
    return {}


standard_tools.originate_command_tool(
    name="originate_vitals",
    description=(
        "Stage a draft Vitals command on the patient's open note. NEVER commits. A "
        "Vitals command records its readings as taken now, so use it only for readings "
        "taken today; never for older readings. Pass at least one reading, in US units."
    ),
    command_class=VitalsCommand,
    fields={
        "height": EffectField(
            type="integer", minimum=10, maximum=108, description="Inches.", editable=True
        ),
        "weight_lbs": EffectField(
            type="integer", minimum=1, maximum=1500, description="Pounds.", editable=True
        ),
        "body_temperature": EffectField(
            type="number", minimum=85, maximum=107, description="Degrees Fahrenheit.", editable=True
        ),
        "blood_pressure_systole": EffectField(
            type="integer", minimum=30, maximum=305, description="Systolic mmHg.", editable=True
        ),
        "blood_pressure_diastole": EffectField(
            type="integer", minimum=20, maximum=180, description="Diastolic mmHg.", editable=True
        ),
        "pulse": EffectField(
            type="integer", minimum=30, maximum=250, description="Beats/min.", editable=True
        ),
        "respiration_rate": EffectField(
            type="integer", minimum=6, maximum=60, description="Breaths/min.", editable=True
        ),
        "oxygen_saturation": EffectField(
            type="integer", minimum=60, maximum=100, description="SpO2 percent.", editable=True
        ),
        "note": EffectField(
            type="string", description="Optional note, up to 150 chars.", editable=True
        ),
    },
    pre_build=_require_a_reading,
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.originate_command_tool(
    name="originate_resolve_condition",
    description=(
        "Stage a draft Resolve Condition command marking one of the patient's conditions "
        "resolved, on the patient's open note. NEVER commits. Requires `condition_id` "
        "from `find_conditions`."
    ),
    command_class=ResolveConditionCommand,
    fields={
        "condition_id": EffectField(
            type="string", description="The condition's `id` from find_conditions.", required=True
        ),
        "rationale": EffectField(
            type="string", description="Why it is resolved, up to 1024 chars.", editable=True
        ),
        "show_in_condition_list": EffectField(
            type="boolean",
            description="Whether it stays on the conditions list as resolved. Defaults to false.",
            editable=True,
        ),
    },
    pre_build=_patients_record_check(Condition, "condition_id", "condition"),
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.originate_command_tool(
    name="originate_remove_allergy",
    description=(
        "Stage a draft Remove Allergy command taking an allergy off the patient's list, "
        "on the patient's open note. NEVER commits. Requires `allergy_id` from "
        "`find_allergies`."
    ),
    command_class=RemoveAllergyCommand,
    fields={
        "allergy_id": EffectField(
            type="string", description="The allergy's `id` from find_allergies.", required=True
        ),
        "narrative": EffectField(
            type="string", description="Why it is removed, up to 512 chars.", editable=True
        ),
    },
    pre_build=_patients_record_check(AllergyIntolerance, "allergy_id", "allergy"),
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.set_progress_labels(
    {
        "originate_medical_history": "Drafting a medical history entry",
        "originate_medication_statement": "Drafting a medication statement",
        "originate_allergy": "Drafting an allergy",
        "originate_family_history": "Drafting a family history entry",
        "originate_surgical_history": "Drafting a surgical history entry",
        "originate_immunization_statement": "Drafting an immunization statement",
        "originate_vitals": "Drafting vitals",
        "originate_resolve_condition": "Drafting a resolved condition",
        "originate_remove_allergy": "Drafting an allergy removal",
    }
)


__exports__ = ()
