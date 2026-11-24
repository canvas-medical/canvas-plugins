"""The history tools: code lookups, and drafts that refuse what would be wrong to stage."""

import json
from collections.abc import Callable
from datetime import date
from typing import Any
from urllib.parse import unquote

import pytest

from canvas_sdk.agents import history_tools, standard_tools
from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    MedicationFactory,
    MedicationStatementFactory,
    PatientFactory,
    PrescriptionFactory,
)
from canvas_sdk.tests.agents.test_standard_tools import _allergy
from canvas_sdk.v1.data import Condition, MedicationCoding

NOTE = "00000000-0000-0000-0000-000000000001"


class _Response:
    def __init__(self, body: Any, status_code: int = 200) -> None:
        self.status_code = status_code
        self._body = body

    def json(self) -> Any:
        return self._body


class _Service:
    """An ontology service answering each path from ``answer``, recording what it was asked."""

    def __init__(self, answer: Callable[[str], Any]) -> None:
        self.answer = answer
        self.paths: list[str] = []

    def get_json(self, path: str) -> _Response:
        self.paths.append(path)
        body = self.answer(path)
        return body if isinstance(body, _Response) else _Response(body)


def _serve(monkeypatch: pytest.MonkeyPatch, name: str, answer: Callable[[str], Any]) -> _Service:
    service = _Service(answer)
    monkeypatch.setattr(history_tools, name, service)
    return service


def _run(tool: str, patient: Any, **arguments: Any) -> tuple[Any, list[Any]]:
    effects: list[Any] = []
    result = standard_tools.execute(
        tool, arguments, ctx={"patient_id": patient.id, "note_id": NOTE, "effects": effects}
    )
    return result, effects


def _data(effect: Any) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(effect.payload)
    return payload


# Looking up codes -------------------------------------------------------------------


def test_medications_come_back_coded_and_obsolete_ones_are_left_out(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An obsolete FDB code stages a blank command, so it is never offered."""
    science = _serve(
        monkeypatch,
        "science_http",
        lambda path: {
            "results": [
                {
                    "med_medication_id": 1,
                    "med_medication_description": "lisinopril 10 mg",
                    "rxnorm_rxcui": "314076",
                    "clinical_quantities": [
                        {
                            "erx_quantity": "1",
                            "clinical_quantity_description": "tablet",
                            "erx_ncpdp_script_quantity_qualifier_code": "C48542",
                            "erx_ncpdp_script_quantity_qualifier_description": "Tablet",
                            "representative_ndc": "00093111101",
                        }
                    ],
                },
                {
                    "med_medication_id": 2,
                    "med_medication_description": "old",
                    "med_medication_status_code": "3",
                },
            ]
        },
    )

    rows = standard_tools.execute(
        "find_clinical_codes", {"kind": "medication", "query": "lisinopril 10"}, ctx={}
    )

    assert rows == [
        {
            "fdb_code": "1",
            "display": "lisinopril 10 mg",
            "rxnorm_rxcui": "314076",
            "clinical_quantities": [
                {
                    "quantity": "1",
                    "description": "tablet",
                    "ncpdp_quantity_qualifier_code": "C48542",
                    "ncpdp_quantity_qualifier_description": "Tablet",
                    "representative_ndc": "00093111101",
                }
            ],
        }
    ]
    assert science.paths == ["/search/grouped-medication/?query=lisinopril%2010&limit=50"]


def test_a_medication_without_dispense_units_has_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """A row with no clinical quantities, or a malformed one, answers an empty list."""
    _serve(
        monkeypatch,
        "science_http",
        lambda path: {
            "results": [
                {"med_medication_id": 1, "med_medication_description": "a"},
                {
                    "med_medication_id": 2,
                    "med_medication_description": "b",
                    "clinical_quantities": [7],
                },
            ]
        },
    )

    rows = standard_tools.execute(
        "find_clinical_codes", {"kind": "medication", "query": "a"}, ctx={}
    )

    assert [row["clinical_quantities"] for row in rows] == [[], []]


@pytest.mark.django_db
def test_a_patients_medications_carry_their_fdb_code() -> None:
    """The code the prescription commands take, whichever coding comes first; none without one."""
    patient = PatientFactory.create()
    coded = MedicationFactory.create(patient=patient)
    for system, code in (
        ("http://www.nlm.nih.gov/research/umls/rxnorm", "314076"),
        ("http://www.fdbhealth.com/", "123456"),
    ):
        MedicationCoding.objects.create(
            medication=coded,
            system=system,
            code=code,
            display="lisinopril 10 mg tablet",
            version="",
            user_selected=False,
        )
    free_text = MedicationFactory.create(patient=patient)
    MedicationCoding.objects.create(
        medication=free_text,
        system="UNSTRUCTURED",
        code="fish oil",
        display="fish oil",
        version="",
        user_selected=False,
    )

    rows, _ = _run("find_medications", patient)

    assert {row["id"]: row["fdb_code"] for row in rows} == {
        str(coded.id): "123456",
        str(free_text.id): None,
    }


def test_allergens_and_vaccines_carry_the_codes_their_commands_take(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each candidate carries exactly the codes its command takes; unusable rows are dropped."""

    def answer(path: str) -> Any:
        if path.startswith("/fdb/allergy/"):
            return [
                {
                    "dam_allergen_concept_id": 900,
                    "dam_allergen_concept_id_type": 2,
                    "dam_allergen_concept_id_description": "penicillin",
                },
                {"dam_allergen_concept_id": 901, "dam_allergen_concept_id_type": 99},
            ]
        return {"results": [{"cvx_code": "115", "cpt_code": "90715", "long_name": "Tdap"}]}

    _serve(monkeypatch, "ontologies_http", answer)

    allergens = standard_tools.execute(
        "find_clinical_codes", {"kind": "allergen", "query": "penicillin"}, ctx={}
    )
    vaccines = standard_tools.execute(
        "find_clinical_codes", {"kind": "immunization", "query": "tdap"}, ctx={}
    )

    assert allergens == [{"concept_id": 900, "concept_type": 2, "display": "penicillin"}]
    assert vaccines == [{"cvx_code": "115", "cpt_code": "90715", "display": "Tdap"}]


def test_a_search_that_does_not_answer_fails_the_tool_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The model is told to try again rather than seeing no candidates."""
    _serve(monkeypatch, "science_http", lambda path: _Response(None, status_code=503))

    with pytest.raises(history_tools.CodeSearchUnavailable):
        standard_tools.execute(
            "find_clinical_codes", {"kind": "surgical_history", "query": "appendectomy"}, ctx={}
        )


# Medical history ---------------------------------------------------------------------


@pytest.mark.django_db
def test_medical_history_sends_text_that_resolves_to_the_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The chart stores the first match for the text, so the text must lead to the code."""
    hits = {
        "Appendicitis": [{"icd10_code": "K37", "icd10_text": "Unspecified appendicitis"}],
        "K35.80": [{"icd10_code": "K35.80", "icd10_text": "Acute appendicitis, unspecified"}],
        "Acute appendicitis, unspecified": [
            {"icd10_code": "K35.80", "icd10_text": "Acute appendicitis, unspecified"}
        ],
    }
    _serve(
        monkeypatch,
        "science_http",
        lambda path: hits[unquote(path.split("query=")[1].split("&")[0])],
    )
    patient = PatientFactory.create()

    result, (effect,) = _run(
        "originate_medical_history", patient, icd10_code="K35.80", display="Appendicitis"
    )

    assert result["ok"] is True
    assert _data(effect)["data"]["past_medical_history"] == "Acute appendicitis, unspecified"


@pytest.mark.django_db
def test_medical_history_refuses_a_code_no_entry_resolves_to(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With no entry for the code, nothing is staged rather than an empty entry."""
    _serve(monkeypatch, "science_http", lambda path: {"results": []})

    with pytest.raises(ValueError, match="No past-medical-history entry resolves to Z99.9"):
        _run("originate_medical_history", PatientFactory.create(), icd10_code="Z99.9")


# Medication statements ---------------------------------------------------------------


def _fdb(schedule: str) -> Callable[[str], Any]:
    def answer(path: str) -> Any:
        if path.startswith("/fdb/grouped-medication/"):
            return {"clinical_quantities": [{"representative_ndc": "00000000001"}]}
        return {"drug_enforcement_administration_code": schedule}

    return answer


@pytest.mark.django_db
def test_a_medication_statement_is_staged_coded(monkeypatch: pytest.MonkeyPatch) -> None:
    """A coded entry keeps drug-interaction checking on."""
    _serve(monkeypatch, "ontologies_http", _fdb("0"))
    patient = PatientFactory.create()

    result, (effect,) = _run(
        "originate_medication_statement",
        patient,
        fdb_code="123456",
        display="lisinopril 10 mg",
        sig="1 tablet daily",
    )

    assert result["ok"] is True and result["command_id"] == _data(effect)["command"]
    data = _data(effect)["data"]
    assert data["sig"] == "1 tablet daily"
    assert data["fdb_code"]["code"] == "123456"
    assert data["fdb_code"]["system"] == "http://www.fdbhealth.com/"


@pytest.mark.parametrize(
    ("schedule", "message"),
    [("2", "Schedule 2 controlled substance"), ("", "Could not confirm")],
)
@pytest.mark.django_db
def test_a_controlled_or_unverifiable_medication_is_refused(
    monkeypatch: pytest.MonkeyPatch, schedule: str, message: str
) -> None:
    """Recording a controlled substance stays the clinician's own entry."""
    _serve(monkeypatch, "ontologies_http", _fdb(schedule))

    with pytest.raises(ValueError, match=message):
        _run("originate_medication_statement", PatientFactory.create(), fdb_code="123456")


@pytest.mark.django_db
def test_a_medication_already_on_the_list_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """A duplicate of an active medication is refused before any lookup."""
    service = _serve(monkeypatch, "ontologies_http", _fdb("0"))
    patient = PatientFactory.create()
    medication = MedicationFactory.create(
        patient=patient, status="active", committer=CanvasUserFactory.create()
    )
    MedicationCoding.objects.create(
        medication=medication,
        system="http://www.fdbhealth.com/",
        code="123456",
        display="lisinopril 10 mg",
        version="",
        user_selected=False,
    )

    with pytest.raises(ValueError, match="already has this medication"):
        _run("originate_medication_statement", patient, fdb_code="123456")
    assert service.paths == [], "the duplicate is caught before any lookup"


# Allergies -----------------------------------------------------------------------------


@pytest.mark.django_db
def test_an_allergy_is_staged_with_its_allergen_and_severity() -> None:
    """The two allergen arguments combine into the command's one allergen field."""
    patient = PatientFactory.create()

    result, (effect,) = _run(
        "originate_allergy", patient, concept_id=900, concept_type=2, severity="severe"
    )

    assert result["ok"] is True
    data = _data(effect)["data"]
    assert data["allergy"] == {"concept_id": 900, "concept_type": 2}
    assert data["severity"] == "severe"


@pytest.mark.django_db
def test_an_allergen_already_on_the_list_is_refused() -> None:
    """An allergen already active on the list, coded as the chart codes it, is refused."""
    patient = PatientFactory.create()
    _allergy(patient, concept_id="900")

    with pytest.raises(ValueError, match="already has this allergen"):
        _run("originate_allergy", patient, concept_id=900, concept_type=2)


# The rest -------------------------------------------------------------------------------


@pytest.mark.django_db
def test_history_entries_are_sent_as_named_codes() -> None:
    """Family history and vaccines go in as codes with their names, not bare strings."""
    patient = PatientFactory.create()

    _, (family,) = _run(
        "originate_family_history",
        patient,
        snomed_code="22298006",
        display="Myocardial infarction",
        relative="father",
    )
    _, (vaccine,) = _run(
        "originate_immunization_statement",
        patient,
        cvx_code="115",
        cpt_code="90715",
        display="Tdap",
    )

    assert _data(family)["data"]["family_history"]["code"] == "22298006"
    assert _data(family)["data"]["relative"] == "father"
    assert _data(vaccine)["data"]["cvx_code"]["system"] == "http://hl7.org/fhir/sid/cvx"
    assert _data(vaccine)["data"]["cpt_code"]["code"] == "90715"


@pytest.mark.django_db
def test_vitals_need_at_least_one_reading() -> None:
    """A Vitals command with no reading is refused."""
    with pytest.raises(ValueError, match="at least one reading"):
        _run("originate_vitals", PatientFactory.create(), note="taken seated")


@pytest.mark.django_db
def test_another_patients_allergy_cannot_be_removed() -> None:
    """The id comes from the model, so it is checked against the run's patient."""
    other = _allergy(PatientFactory.create())

    with pytest.raises(ValueError, match="not found for this patient"):
        _run("originate_remove_allergy", PatientFactory.create(), allergy_id=str(other.id))


def _active_condition(patient: Any) -> Any:
    return Condition.objects.create(
        patient=patient,
        deleted=False,
        onset_date=date(2020, 1, 1),
        resolution_date=date(2020, 1, 1),
        clinical_status="active",
        notes="",
        surgical=False,
        committer=CanvasUserFactory.create(),
    )


@pytest.mark.django_db
def test_resolving_another_patients_condition_is_refused() -> None:
    """A condition id the model read elsewhere cannot resolve a condition off this chart."""
    patient = PatientFactory.create()
    theirs = _active_condition(PatientFactory.create())

    with pytest.raises(ValueError, match="condition"):
        _run("originate_resolve_condition", patient, condition_id=str(theirs.id))

    _result, effects = _run(
        "originate_resolve_condition", patient, condition_id=str(_active_condition(patient).id)
    )
    assert len(effects) == 1


def _coded_twice(patient: Any) -> Any:
    """A medication with an RxNorm coding and an FDB coding, both named the same."""
    medication = MedicationFactory.create(patient=patient)
    for system, code in (
        ("http://www.nlm.nih.gov/research/umls/rxnorm", "314076"),
        ("http://www.fdbhealth.com/", "123456"),
    ):
        MedicationCoding.objects.create(
            medication=medication,
            system=system,
            code=code,
            display="lisinopril 10 mg tablet",
            version="",
            user_selected=False,
        )
    return medication


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("tool", "seed"),
    [
        ("find_medications", lambda patient, medication: None),
        (
            "find_prescriptions",
            lambda patient, medication: PrescriptionFactory.create(
                patient=patient, committer=CanvasUserFactory.create(), medication=medication
            ),
        ),
        (
            "find_medication_statements",
            lambda patient, medication: MedicationStatementFactory.create(
                patient=patient, committer=CanvasUserFactory.create(), medication=medication
            ),
        ),
    ],
)
def test_a_medication_found_by_name_comes_back_once_with_its_fdb_code(
    tool: str, seed: Callable[[Any, Any], Any]
) -> None:
    """Two codings carrying the name match the search once, not once per coding."""
    patient = PatientFactory.create()
    medication = _coded_twice(patient)
    seed(patient, medication)

    rows, _ = _run(tool, patient, name_contains="lisinopril")

    assert [row["fdb_code"] for row in rows] == ["123456"]
