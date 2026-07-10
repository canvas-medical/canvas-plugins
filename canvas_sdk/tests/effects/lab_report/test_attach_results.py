"""Tests for ``LabReport.attach_results`` + the ``LabTest`` / ``LabValue`` / ``ObservationStatus`` types."""

import json
from uuid import UUID

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.lab_report import (
    AbnormalFlag,
    LabReport,
    LabTest,
    LabValue,
    ObservationStatus,
)
from canvas_sdk.effects.observation.base import CodingData

REPORT_ID_STR = "123e4567-e89b-12d3-a456-426614174000"
REPORT_ID = UUID(REPORT_ID_STR)
LOINC = "http://loinc.org"


def test_attach_results_emits_effect_with_nested_tests_and_values() -> None:
    """attach_results() emits ATTACH_LAB_REPORT_RESULTS with tests grouping values + LOINC codings."""
    effect = LabReport(external_id="myplugin:ocr-44").attach_results(
        [
            LabTest(
                ontology_test_code="CBC",
                ontology_test_name="Complete Blood Count",
                codings=[CodingData(code="58410-2", display="CBC panel", system=LOINC)],
                values=[
                    LabValue(
                        value="14.2",
                        units="g/dL",
                        reference_range="13.5-17.5",
                        codings=[CodingData(code="718-7", display="Hemoglobin", system=LOINC)],
                    )
                ],
            )
        ]
    )

    assert effect.type == EffectType.ATTACH_LAB_REPORT_RESULTS
    data = json.loads(effect.payload)["data"]
    assert data["external_id"] == "myplugin:ocr-44"
    assert data["report_id"] == ""
    assert data["lab_tests"] == [
        {
            "ontology_test_code": "CBC",
            "ontology_test_name": "Complete Blood Count",
            "codings": [
                {
                    "code": "58410-2",
                    "display": "CBC panel",
                    "system": LOINC,
                    "version": "",
                    "user_selected": False,
                }
            ],
            "values": [
                {
                    "value": "14.2",
                    "units": "g/dL",
                    "reference_range": "13.5-17.5",
                    "abnormal_flag": "",
                    "observation_status": "final",
                    "comment": "",
                    "codings": [
                        {
                            "code": "718-7",
                            "display": "Hemoglobin",
                            "system": LOINC,
                            "version": "",
                            "user_selected": False,
                        }
                    ],
                }
            ],
        }
    ]


def test_attach_results_by_report_id() -> None:
    """attach_results() supports the Canvas report_id (uuid) handle."""
    effect = LabReport(report_id=REPORT_ID).attach_results(
        [LabTest(ontology_test_name="CBC", values=[LabValue(value="14.2")])]
    )
    data = json.loads(effect.payload)["data"]
    assert data["report_id"] == REPORT_ID_STR
    assert data["external_id"] == ""


def test_attach_results_codings_default_to_none() -> None:
    """A test/value without codings serializes codings as None (no LOINC attached)."""
    effect = LabReport(external_id="x").attach_results(
        [LabTest(ontology_test_name="CBC", values=[LabValue(value="14.2")])]
    )
    test = json.loads(effect.payload)["data"]["lab_tests"][0]
    assert test["codings"] is None
    assert test["values"][0]["codings"] is None


def test_attach_results_requires_a_handle() -> None:
    """attach_results() fails when the report has no handle."""
    with pytest.raises(ValidationError):
        LabReport().attach_results([LabTest(values=[LabValue(value="14.2")])])


def test_attach_results_rejects_both_handles() -> None:
    """attach_results() fails when both handles are set (ambiguous)."""
    with pytest.raises(ValidationError):
        LabReport(report_id=REPORT_ID, external_id="x").attach_results(
            [LabTest(values=[LabValue(value="14.2")])]
        )


def test_attach_results_requires_at_least_one_test() -> None:
    """attach_results() fails on an empty test list (pydantic min_length)."""
    with pytest.raises(ValidationError):
        LabReport(external_id="myplugin:ocr-44").attach_results([])


def test_lab_test_requires_at_least_one_value() -> None:
    """A LabTest with no values is rejected (pydantic min_length)."""
    with pytest.raises(ValidationError):
        LabTest(ontology_test_name="CBC", values=[])


def test_lab_value_has_no_test_code_fields() -> None:
    """Order/compendium codes live on LabTest, never on LabValue (jrwils review)."""
    assert "ontology_test_code" not in LabValue.model_fields
    assert "ontology_test_name" not in LabValue.model_fields
    assert "ontology_test_code" in LabTest.model_fields
    assert "ontology_test_name" in LabTest.model_fields


def test_lab_value_defaults() -> None:
    """LabValue defaults observation_status to the FINAL enum member."""
    lab_value = LabValue(value="14.2")
    assert lab_value.observation_status is ObservationStatus.FINAL
    assert lab_value.to_dict()["observation_status"] == "final"


def test_lab_value_rejects_invalid_status() -> None:
    """observation_status only accepts ObservationStatus values."""
    with pytest.raises(ValidationError):
        LabValue(
            value="14.2",
            observation_status="bogus",  # type: ignore[arg-type]  # testing runtime rejection
        )


def test_observation_status_covers_fhir_value_set() -> None:
    """ObservationStatus mirrors the home-app/FHIR observation-status value set."""
    assert {status.value for status in ObservationStatus} == {
        "amended",
        "cancelled",
        "corrected",
        "entered-in-error",
        "final",
        "preliminary",
        "registered",
        "unknown",
    }


def test_lab_value_accepts_registered_status() -> None:
    """observation_status accepts the full set, e.g. REGISTERED."""
    lab_value = LabValue(value="14.2", observation_status=ObservationStatus.REGISTERED)
    assert lab_value.to_dict()["observation_status"] == "registered"


def test_abnormal_flag_defaults_to_empty() -> None:
    """abnormal_flag defaults to None and serializes to an empty string."""
    assert LabValue(value="14.2").abnormal_flag is None
    assert LabValue(value="14.2").to_dict()["abnormal_flag"] == ""


def test_abnormal_flag_serializes_enum_value() -> None:
    """A set abnormal_flag serializes to its HL7 code; a raw code string is coerced."""
    assert LabValue(value="14.2", abnormal_flag=AbnormalFlag.HIGH).to_dict()["abnormal_flag"] == "H"
    assert LabValue(value="14.2", abnormal_flag="LL").to_dict()["abnormal_flag"] == "LL"  # type: ignore[arg-type]


def test_abnormal_flag_rejects_invalid_code() -> None:
    """abnormal_flag only accepts AbnormalFlag values."""
    with pytest.raises(ValidationError):
        LabValue(value="14.2", abnormal_flag="banana")  # type: ignore[arg-type]  # runtime rejection
