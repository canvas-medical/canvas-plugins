"""Tests for ``LabReport.attach_results`` + the ``LabValue`` / ``ObservationStatus`` types."""

import json
from uuid import UUID

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.lab_report import LabReport, LabValue, ObservationStatus

REPORT_ID_STR = "123e4567-e89b-12d3-a456-426614174000"
REPORT_ID = UUID(REPORT_ID_STR)


def test_attach_results_emits_effect_with_values() -> None:
    """attach_results() emits ATTACH_LAB_REPORT_RESULTS with serialized lab values."""
    effect = LabReport(external_id="myplugin:ocr-44").attach_results(
        [
            LabValue(
                ontology_test_code="718-7",
                ontology_test_name="Hemoglobin",
                value="14.2",
                units="g/dL",
                reference_range="13.5-17.5",
            )
        ]
    )

    assert effect.type == EffectType.ATTACH_LAB_REPORT_RESULTS
    data = json.loads(effect.payload)["data"]
    assert data["external_id"] == "myplugin:ocr-44"
    assert data["report_id"] == ""
    assert data["lab_values"] == [
        {
            "ontology_test_code": "718-7",
            "ontology_test_name": "Hemoglobin",
            "value": "14.2",
            "units": "g/dL",
            "reference_range": "13.5-17.5",
            "abnormal_flag": "",
            "observation_status": "final",
            "comment": "",
        }
    ]


def test_attach_results_by_report_id() -> None:
    """attach_results() supports the Canvas report_id (uuid) handle."""
    effect = LabReport(report_id=REPORT_ID).attach_results(
        [LabValue(ontology_test_code="718-7", value="14.2")]
    )
    data = json.loads(effect.payload)["data"]
    assert data["report_id"] == REPORT_ID_STR
    assert data["external_id"] == ""


def test_attach_results_requires_a_handle() -> None:
    """attach_results() fails when the report has no handle."""
    with pytest.raises(ValidationError):
        LabReport().attach_results([LabValue(ontology_test_code="718-7", value="14.2")])


def test_attach_results_rejects_both_handles() -> None:
    """attach_results() fails when both handles are set (ambiguous)."""
    with pytest.raises(ValidationError):
        LabReport(report_id=REPORT_ID, external_id="x").attach_results(
            [LabValue(ontology_test_code="718-7", value="14.2")]
        )


def test_attach_results_requires_at_least_one_value() -> None:
    """attach_results() fails on an empty value list (pydantic min_length)."""
    with pytest.raises(ValidationError):
        LabReport(external_id="myplugin:ocr-44").attach_results([])


def test_lab_value_defaults() -> None:
    """LabValue defaults observation_status to the FINAL enum member."""
    lab_value = LabValue(ontology_test_code="718-7", value="14.2")
    assert lab_value.observation_status is ObservationStatus.FINAL
    assert lab_value.values["observation_status"] == "final"


def test_lab_value_rejects_invalid_status() -> None:
    """observation_status only accepts ObservationStatus values."""
    with pytest.raises(ValidationError):
        LabValue(
            ontology_test_code="718-7",
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
    lab_value = LabValue(
        ontology_test_code="718-7", value="14.2", observation_status=ObservationStatus.REGISTERED
    )
    assert lab_value.values["observation_status"] == "registered"
