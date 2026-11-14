"""The intake tools: read an incoming document and suggest how it is filed, never more."""

import json
from datetime import date
from typing import Any

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.agents import document_tools, standard_tools
from canvas_sdk.agents.document_tools import MAX_DOCUMENT_TYPES
from canvas_sdk.test_utils.factories import (
    DocumentTypeFactory,
    IntegrationTaskFactory,
    LabReportTemplateFactory,
    LabReportTemplateFieldFactory,
    PatientFactory,
    StaffFactory,
    TeamFactory,
)
from canvas_sdk.v1.data import PatientExternalIdentifier
from canvas_sdk.v1.data.integration_task import IntegrationTaskStatus

BIRTH = date(1980, 4, 2)


def _run(tool: str, document: Any, **arguments: Any) -> tuple[Any, list[Any]]:
    effects: list[Any] = []
    ctx = {"document_id": str(document.id), "effects": effects, "gateway": object()}
    return standard_tools.execute(tool, arguments, ctx=ctx), effects


def _sent(effect: Any) -> tuple[str, dict[str, Any]]:
    return EffectType.Name(effect.type), json.loads(effect.payload)["data"]


@pytest.fixture
def document() -> Any:
    """An unfiled fax in the queue."""
    return IntegrationTaskFactory.create(patient=None)


# Reading the document ------------------------------------------------------------------


@pytest.mark.django_db
def test_the_run_reads_its_own_document(monkeypatch: pytest.MonkeyPatch, document: Any) -> None:
    """The file read is the run's document's, asked the model's question."""
    asked: dict[str, Any] = {}

    def answer(holder: Any, question: str, **kwargs: Any) -> dict[str, Any]:
        asked.update(holder=holder, question=question)
        return {"ok": True, "answer": "Jane Doe, DOB 1980-04-02 (page 1)", "note": "data"}

    monkeypatch.setattr(document_tools, "answer_from_file", answer)
    document.document = "faxes/1.pdf"
    document.save()

    result, effects = _run("read_incoming_document", document, question="Who is it for?")

    assert asked == {"holder": document, "question": "Who is it for?"}
    assert result["answer"].startswith("Jane Doe") and result["document_id"] == str(document.id)
    assert effects == []


@pytest.mark.django_db
def test_a_junked_document_is_not_read(document: Any) -> None:
    """A document staff junked is out of the queue."""
    document.status = IntegrationTaskStatus.JUNK
    document.save()

    with pytest.raises(ValueError, match="not in the queue"):
        _run("read_incoming_document", document, question="Who is it for?")


@pytest.mark.parametrize(
    "tool", ["read_incoming_document", "match_patient", "suggest_patient", "categorize_document"]
)
@pytest.mark.django_db
def test_a_run_about_no_document_has_no_intake_tools(tool: str) -> None:
    """The document comes from the run, never from the model."""
    with pytest.raises(ValueError, match="not about an incoming document"):
        standard_tools.execute(
            tool, {"question": "x", "mrn": "1", "document_type_key": "x"}, ctx={"effects": []}
        )


# Matching the patient -------------------------------------------------------------------


@pytest.mark.django_db
def test_one_matching_patient_is_named(document: Any) -> None:
    """Name and birth date that fit exactly one patient name them."""
    patient = PatientFactory.create(first_name="Jane", last_name="Doe", birth_date=BIRTH)
    PatientFactory.create(first_name="Jane", last_name="Doe", birth_date=date(1990, 1, 1))

    result, _ = _run(
        "match_patient", document, first_name=" jane", last_name="DOE", birth_date="1980-04-02"
    )

    assert result["match"]["patient_id"] == str(patient.id)
    assert result["matched_on"] == "last_name, birth_date, first_name"
    assert result["confidence"] == "high"


@pytest.mark.django_db
def test_several_matching_patients_name_no_one(document: Any) -> None:
    """Choosing among near matches is a person's call, so no candidate is shown."""
    for _ in range(2):
        PatientFactory.create(first_name="Jane", last_name="Doe", birth_date=BIRTH)

    result, _ = _run("match_patient", document, last_name="Doe", birth_date="1980-04-02")

    assert result == {
        "match": None,
        "reason": "More than one patient matches; a person chooses, so none is suggested.",
    }


@pytest.mark.django_db
def test_a_nickname_matches_the_first_name(document: Any) -> None:
    """A document can use the name the patient goes by."""
    patient = PatientFactory.create(
        first_name="Margaret", nickname="Peggy", last_name="Doe", birth_date=BIRTH
    )

    result, _ = _run(
        "match_patient", document, first_name="Peggy", last_name="Doe", birth_date="1980-04-02"
    )

    assert result["match"]["patient_id"] == str(patient.id)


@pytest.mark.django_db
def test_an_mrn_must_agree_with_the_rest(document: Any) -> None:
    """An MRN whose patient has another birth date matches no one."""
    patient = PatientFactory.create(last_name="Doe", birth_date=BIRTH)

    agreeing, _ = _run("match_patient", document, mrn=patient.mrn, last_name="doe")
    disagreeing, _ = _run("match_patient", document, mrn=patient.mrn, birth_date="1999-09-09")

    assert agreeing == {
        "match": {"patient_id": str(patient.id)},
        "matched_on": "mrn, last_name",
        "confidence": "medium",
    }
    assert disagreeing["match"] is None


@pytest.mark.django_db
def test_an_mrn_alone_names_no_one(document: Any) -> None:
    """A model fed a made-up MRN cannot learn whose it is."""
    patient = PatientFactory.create()

    with pytest.raises(ValueError, match="last name or birth date with the MRN"):
        _run("match_patient", document, mrn=patient.mrn)


@pytest.mark.django_db
def test_a_name_alone_is_not_enough(document: Any) -> None:
    """Without an MRN, the last name and birth date are both required."""
    with pytest.raises(ValueError, match="last name and birth date"):
        _run("match_patient", document, first_name="Jane", last_name="Doe")


@pytest.mark.django_db
def test_the_suggested_patient_is_the_one_code_matched(document: Any) -> None:
    """The model passes what the document says, never a patient id."""
    patient = PatientFactory.create(last_name="Doe", birth_date=BIRTH)

    result, (effect,) = _run(
        "suggest_patient", document, last_name="Doe", birth_date="1980-04-02", label="From fax"
    )

    assert result["ok"] is True
    assert _sent(effect) == (
        "LINK_DOCUMENT_TO_PATIENT",
        {
            "document_id": str(document.id),
            "patient_key": str(patient.id),
            "annotations": [
                {"text": "AI suggested", "color": document_tools.SOURCE_COLOR},
                {"text": "Match: medium", "color": document_tools.CONFIDENCE_COLORS["medium"]},
                {"text": "From fax", "color": document_tools.SOURCE_COLOR},
            ],
        },
    )


@pytest.mark.django_db
def test_no_patient_is_suggested_without_one_match(document: Any) -> None:
    """With no match, nothing is staged."""
    result, effects = _run("suggest_patient", document, last_name="Nobody", birth_date="1980-04-02")

    assert result["ok"] is False and effects == []


# Document types and templates ------------------------------------------------------------


@pytest.mark.django_db
def test_document_types_are_capped(document: Any) -> None:
    """One search returns at most MAX_DOCUMENT_TYPES, first by name."""
    DocumentTypeFactory.create_batch(MAX_DOCUMENT_TYPES + 1)

    listed, _ = _run("find_document_types", document)

    assert len(listed) == MAX_DOCUMENT_TYPES
    assert [t["name"] for t in listed] == sorted(t["name"] for t in listed)


@pytest.mark.django_db
def test_document_types_are_listed_and_suggested(document: Any) -> None:
    """A type is suggested by its key, as Canvas defines it."""
    lab = DocumentTypeFactory.create(
        name="Lab Report", report_type="CLINICAL", template_type="LabReportTemplate"
    )
    DocumentTypeFactory.create(name="Referral Form")

    listed, _ = _run("find_document_types", document, query="lab")
    result, (effect,) = _run("categorize_document", document, document_type_key=lab.key)

    assert listed == [
        {
            "key": lab.key,
            "name": "Lab Report",
            "report_type": "CLINICAL",
            "template_type": "LabReportTemplate",
        }
    ]
    assert _sent(effect)[1]["document_type"] == {
        "key": lab.key,
        "name": "Lab Report",
        "report_type": "CLINICAL",
        "template_type": "LabReportTemplate",
    }
    with pytest.raises(ValueError, match="No document type"):
        _run("categorize_document", document, document_type_key="made-up")


@pytest.mark.django_db
def test_templates_list_their_fields_in_order(document: Any) -> None:
    """Values can only be filled into fields the template has."""
    template = LabReportTemplateFactory.create(name="Lipid Panel", search_keywords="")
    LabReportTemplateFieldFactory.create(
        report_template=template, sequence=2, code="2093-3", label="Cholesterol"
    )
    LabReportTemplateFieldFactory.create(
        report_template=template, sequence=1, code="", label="Fasting"
    )

    (found,), _ = _run("find_report_templates", document, template_type="lab", query="lipid")

    assert found["template_id"] == template.dbid
    assert [(f["code"], f["label"]) for f in found["fields"]] == [
        (None, "Fasting"),
        ("2093-3", "Cholesterol"),
    ]


# Prefilling values ------------------------------------------------------------------------


@pytest.mark.django_db
def test_values_are_filled_into_the_templates_own_fields(document: Any) -> None:
    """Fields are keyed by code, or by label when they have none, whichever the model used."""
    template = LabReportTemplateFactory.create(name="Lipid Panel")
    LabReportTemplateFieldFactory.create(
        report_template=template, code="2093-3", label="Cholesterol"
    )
    LabReportTemplateFieldFactory.create(report_template=template, code="", label="Fasting")

    result, (effect,) = _run(
        "prefill_document_fields",
        document,
        template_type="lab",
        template_id=template.dbid,
        fields={
            "cholesterol": {"value": " 212 ", "unit": "mg/dL", "abnormal": True},
            "Fasting": {"value": "yes"},
        },
    )

    assert result["filled"] == ["2093-3", "Fasting"]
    assert _sent(effect)[1]["templates"] == [
        {
            "template_id": template.dbid,
            "template_name": "Lipid Panel",
            "fields": {
                "2093-3": {"value": "212", "unit": "mg/dL", "abnormal": True},
                "Fasting": {"value": "yes"},
            },
        }
    ]


@pytest.mark.django_db
def test_a_field_the_template_lacks_is_refused(document: Any) -> None:
    """A value with nowhere to go is refused rather than dropped."""
    template = LabReportTemplateFactory.create(name="Lipid Panel")
    LabReportTemplateFieldFactory.create(report_template=template, code="2093-3")

    with pytest.raises(ValueError, match="has no field LDL"):
        _run(
            "prefill_document_fields",
            document,
            template_type="lab",
            template_id=template.dbid,
            fields={"LDL": {"value": "140"}},
        )


@pytest.mark.django_db
def test_an_inactive_template_is_refused(document: Any) -> None:
    """Only templates the practice uses take values."""
    template = LabReportTemplateFactory.create(active=False)

    with pytest.raises(ValueError, match="No active lab template"):
        _run(
            "prefill_document_fields",
            document,
            template_type="lab",
            template_id=template.dbid,
            fields={"x": {"value": "1"}},
        )


# Reviewers ---------------------------------------------------------------------------------


@pytest.mark.django_db
def test_a_reviewer_is_suggested_with_review_still_required(document: Any) -> None:
    """The agent routes the review; it never marks a document reviewed."""
    staff = StaffFactory.create()
    team = TeamFactory.create()

    _, (effect,) = _run(
        "assign_document_reviewer", document, staff_id=str(staff.id), team_id=str(team.id)
    )

    data = _sent(effect)[1]
    assert (data["reviewer_id"], data["team_id"], data["review_mode"]) == (
        str(staff.id),
        str(team.id),
        "RR",
    )


@pytest.mark.django_db
def test_an_inactive_reviewer_is_refused(document: Any) -> None:
    """An inactive staff member cannot review."""
    staff = StaffFactory.create(active=False)

    with pytest.raises(ValueError, match="No active staff member"):
        _run("assign_document_reviewer", document, staff_id=str(staff.id))


def _sending_mrn(
    patient: Any,
    value: str,
    *,
    identifier_type: str = "MR",
    system: str = "https://valley-lab.example/mrn",
    expires: date = date(2099, 1, 1),
) -> None:
    """An identifier an outside organization keeps for ``patient``, by default its MRN."""
    PatientExternalIdentifier.objects.create(
        patient=patient,
        use="usual",
        identifier_type=identifier_type,
        system=system,
        value=value,
        issued_date=date(2020, 1, 1),
        expiration_date=expires,
    )


@pytest.mark.django_db
def test_the_sending_organizations_mrn_matches(document: Any) -> None:
    """A fax carries the lab's MRN for the patient, kept as an external identifier."""
    patient = PatientFactory.create(first_name="Jane", last_name="Doe", birth_date=BIRTH)
    _sending_mrn(patient, "VL-4471")

    full, _ = _run(
        "match_patient",
        document,
        mrn="VL-4471",
        first_name="Jane",
        last_name="Doe",
        birth_date="1980-04-02",
    )
    names_only, _ = _run(
        "match_patient", document, mrn="VL-4471", last_name="Doe", birth_date="1980-04-02"
    )

    assert full == {
        "match": {"patient_id": str(patient.id)},
        "matched_on": "sending_mrn, last_name, birth_date, first_name",
        "confidence": "high",
    }
    # Another organization's MRN never raises the confidence on its own.
    assert names_only["confidence"] == "medium"


@pytest.mark.django_db
def test_the_sending_organizations_mrn_must_agree_too(document: Any) -> None:
    """Another organization's MRN counts only with both last name and birth date agreeing."""
    patient = PatientFactory.create(last_name="Doe", birth_date=BIRTH)
    _sending_mrn(patient, "VL-4471")

    disagreeing, _ = _run("match_patient", document, mrn="VL-4471", birth_date="1999-09-09")
    one_agreeing, _ = _run("match_patient", document, mrn="VL-4471", birth_date="1980-04-02")

    assert disagreeing["match"] is None
    assert one_agreeing["match"] is None
    with pytest.raises(ValueError, match="last name or birth date with the MRN"):
        _run("match_patient", document, mrn="VL-4471")


@pytest.mark.django_db
def test_type_and_values_carry_the_models_confidence(document: Any) -> None:
    """The reviewer sees how sure the model was, colored by level."""
    lab = DocumentTypeFactory.create(name="Lab Report", report_type="CLINICAL")
    template = LabReportTemplateFactory.create(name="Lipid Panel")
    LabReportTemplateFieldFactory.create(report_template=template, code="2093-3")

    _, (categorized,) = _run(
        "categorize_document", document, document_type_key=lab.key, confidence="high"
    )
    _, (prefilled,) = _run(
        "prefill_document_fields",
        document,
        template_type="lab",
        template_id=template.dbid,
        fields={"2093-3": {"value": "212"}},
        confidence="low",
    )

    assert _sent(categorized)[1]["annotations"] == [
        {"text": "AI suggested", "color": document_tools.SOURCE_COLOR},
        {"text": "AI: high", "color": document_tools.CONFIDENCE_COLORS["high"]},
    ]
    assert _sent(prefilled)[1]["annotations"][1] == {
        "text": "AI: low",
        "color": document_tools.CONFIDENCE_COLORS["low"],
    }


@pytest.mark.parametrize(
    "identifier",
    [
        {"identifier_type": "MB", "system": "https://payer.example/member"},
        {"expires": date(2021, 1, 1)},
    ],
    ids=["not a medical record number", "expired"],
)
@pytest.mark.django_db
def test_only_a_current_medical_record_number_counts(document: Any, identifier: Any) -> None:
    """An insurance member id or an expired MRN with the same value is not an MRN match."""
    patient = PatientFactory.create(last_name="Doe", birth_date=BIRTH)
    PatientFactory.create(last_name="Doe", birth_date=BIRTH)
    _sending_mrn(patient, "VL-4471", **identifier)

    result, _ = _run(
        "match_patient", document, mrn="VL-4471", last_name="Doe", birth_date="1980-04-02"
    )

    assert result["match"] is None


@pytest.mark.django_db
def test_a_printed_sending_mrn_is_confirmed_against_the_patients_record(document: Any) -> None:
    """The print's MRN can be the lab's, which the patient's current identifier confirms."""
    patient = PatientFactory.create(first_name="Jane", last_name="Doe", birth_date=BIRTH)
    _sending_mrn(patient, "VL-4471")
    _sending_mrn(patient, "VL-9999", expires=date(2000, 1, 1))
    read = {"first_name": "Jane", "last_name": "Doe", "birth_date": "1980-04-02"}
    printed = {"name": "DOE, JANE", "birth_date": "04/02/1980"}

    current, _ = _run(
        "match_patient",
        document,
        **read,
        mrn="VL-4471",
        as_printed={**printed, "mrn": "MRN VL-4471"},
        legibility="clear",
    )
    expired, _ = _run(
        "match_patient",
        document,
        **read,
        mrn="VL-9999",
        as_printed={**printed, "mrn": "MRN VL-9999"},
        legibility="clear",
    )

    assert current["match"] == {"patient_id": str(patient.id)}
    assert expired["match"] is None
