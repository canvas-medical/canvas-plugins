"""Round-trip + validation tests for the ``LabReportAttachResults`` effect.

This effect attaches lab tests/values to an existing report after the
fact (the async-OCR case). It pins the wire shape and the handle/value
guards.
"""

import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.lab_report import LabReportAttachResults, LabValue


def test_attach_emits_effect_with_values() -> None:
    """apply() emits ATTACH_LAB_REPORT_RESULTS with serialized lab values."""
    effect = LabReportAttachResults(
        external_id="myplugin:ocr-44",
        lab_values=[
            LabValue(
                ontology_test_code="718-7",
                ontology_test_name="Hemoglobin",
                value="14.2",
                units="g/dL",
                reference_range="13.5-17.5",
            ),
        ],
    ).apply()

    assert effect.type == EffectType.ATTACH_LAB_REPORT_RESULTS
    payload = json.loads(effect.payload)
    assert payload["data"]["external_id"] == "myplugin:ocr-44"
    assert payload["data"]["report_id"] == ""
    assert payload["data"]["lab_values"] == [
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


def test_attach_by_report_id() -> None:
    """apply() supports the Canvas report_id handle."""
    effect = LabReportAttachResults(
        report_id="canvas-uuid",
        lab_values=[LabValue(ontology_test_code="718-7", value="14.2")],
    ).apply()

    payload = json.loads(effect.payload)
    assert payload["data"]["report_id"] == "canvas-uuid"
    assert payload["data"]["external_id"] == ""


def test_attach_requires_a_handle() -> None:
    """apply() fails without report_id or external_id."""
    with pytest.raises(ValidationError):
        LabReportAttachResults(
            lab_values=[LabValue(ontology_test_code="718-7", value="14.2")],
        ).apply()


def test_attach_rejects_both_handles() -> None:
    """apply() fails when both handles are supplied (ambiguous)."""
    with pytest.raises(ValidationError):
        LabReportAttachResults(
            report_id="canvas-uuid",
            external_id="myplugin:ocr-44",
            lab_values=[LabValue(ontology_test_code="718-7", value="14.2")],
        ).apply()


def test_attach_requires_at_least_one_value() -> None:
    """apply() fails with an empty value list (nothing to attach)."""
    with pytest.raises(ValidationError):
        LabReportAttachResults(external_id="myplugin:ocr-44", lab_values=[]).apply()


def test_lab_value_defaults() -> None:
    """LabValue applies sensible defaults for optional fields."""
    lab_value = LabValue(ontology_test_code="718-7", value="14.2")

    assert lab_value.values == {
        "ontology_test_code": "718-7",
        "ontology_test_name": "",
        "value": "14.2",
        "units": "",
        "reference_range": "",
        "abnormal_flag": "",
        "observation_status": "final",
        "comment": "",
    }
