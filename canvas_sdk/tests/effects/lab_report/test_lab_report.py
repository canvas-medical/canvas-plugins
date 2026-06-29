"""Tests for the fluent ``LabReport`` SDK effect (create / update / enter-in-error)."""

import datetime
import json
from uuid import UUID

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.lab_report import LabReport

REPORT_ID_STR = "123e4567-e89b-12d3-a456-426614174000"
REPORT_ID = UUID(REPORT_ID_STR)


# --- create ---------------------------------------------------------------


def test_create_real_round_trip() -> None:
    """create() emits CREATE_LAB_REPORT with the dirty fields."""
    effect = LabReport(
        external_id="myplugin:ocr-44",
        patient_id="29cc62645764b7c4b16a2459",
        report_name="CBC scanned 2026-06-17",
        date_performed=datetime.datetime(2026, 6, 17, 8, 15, 0),
    ).create()

    assert effect.type == EffectType.CREATE_LAB_REPORT
    data = json.loads(effect.payload)["data"]
    assert data["external_id"] == "myplugin:ocr-44"
    assert data["patient_id"] == "29cc62645764b7c4b16a2459"
    assert data["report_name"] == "CBC scanned 2026-06-17"
    assert data["date_performed"] == "2026-06-17T08:15:00"


def test_create_requires_patient_id() -> None:
    """create() fails without patient_id."""
    with pytest.raises(ValidationError):
        LabReport(external_id="myplugin:ocr-44").create()


def test_create_requires_external_id() -> None:
    """create() fails without the plugin's external_id handle."""
    with pytest.raises(ValidationError):
        LabReport(patient_id="29cc62645764b7c4b16a2459").create()


def test_create_forbids_report_id() -> None:
    """create() fails when a Canvas report_id is supplied (creation assigns it)."""
    with pytest.raises(ValidationError):
        LabReport(report_id=REPORT_ID, patient_id="p", external_id="x").create()


def test_external_id_max_length_enforced() -> None:
    """external_id over 40 chars is rejected by pydantic at construction."""
    with pytest.raises(ValidationError):
        LabReport(external_id="a" * 41, patient_id="p")


# --- update ---------------------------------------------------------------


def test_update_emits_dirty_fields_only() -> None:
    """update() carries only the fields that were set."""
    effect = LabReport(external_id="myplugin:ocr-44", report_name="Complete Blood Count").update()

    assert effect.type == EffectType.UPDATE_LAB_REPORT
    data = json.loads(effect.payload)["data"]
    assert data["external_id"] == "myplugin:ocr-44"
    assert data["report_name"] == "Complete Blood Count"
    assert "patient_id" not in data


def test_update_accepts_report_id_uuid_string() -> None:
    """report_id accepts a uuid string (Field strict=False) and serializes as a string."""
    effect = LabReport(
        report_id=REPORT_ID_STR,  # type: ignore[arg-type]  # exercising uuid-string coercion
        report_name="x",
    ).update()
    assert json.loads(effect.payload)["data"]["report_id"] == REPORT_ID_STR


def test_update_requires_a_handle() -> None:
    """update() fails without report_id or external_id."""
    with pytest.raises(ValidationError):
        LabReport(report_name="x").update()


def test_update_requires_a_mutable_field() -> None:
    """update() fails when a handle is given but nothing to change."""
    with pytest.raises(ValidationError):
        LabReport(external_id="myplugin:ocr-44").update()


def test_update_does_not_check_existence() -> None:
    """update() no longer hits the data layer, so a create→update chain is allowed."""
    effect = LabReport(external_id="never-persisted-yet", report_name="x").update()
    assert effect.type == EffectType.UPDATE_LAB_REPORT


# --- enter in error -------------------------------------------------------


def test_enter_in_error_emits_handle_only() -> None:
    """enter_in_error() emits ENTER_IN_ERROR_LAB_REPORT with only the external_id handle."""
    effect = LabReport(external_id="myplugin:ocr-44").enter_in_error()

    assert effect.type == EffectType.ENTER_IN_ERROR_LAB_REPORT
    assert json.loads(effect.payload) == {"data": {"external_id": "myplugin:ocr-44"}}


def test_enter_in_error_by_report_id() -> None:
    """enter_in_error() supports the Canvas report_id handle."""
    effect = LabReport(report_id=REPORT_ID).enter_in_error()
    assert json.loads(effect.payload) == {"data": {"report_id": REPORT_ID_STR}}


def test_enter_in_error_ignores_extra_fields() -> None:
    """Extra fields are ignored (not rejected); only the handle is sent."""
    effect = LabReport(
        external_id="myplugin:ocr-44", report_name="ignored", patient_id="p"
    ).enter_in_error()
    assert json.loads(effect.payload) == {"data": {"external_id": "myplugin:ocr-44"}}


def test_enter_in_error_requires_a_handle() -> None:
    """enter_in_error() fails without a handle."""
    with pytest.raises(ValidationError):
        LabReport().enter_in_error()
