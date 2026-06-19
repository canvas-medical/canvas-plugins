"""Round-trip + validation tests for the fluent ``LabReport`` SDK effect.

These pin the wire shape (proto enum, payload key set, dirty-field
serialization) and the per-method validation guards for the report
lifecycle: create (decoupled), update (rename/metadata), and
enter-in-error.
"""

import datetime
import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.lab_report.base import LabReport


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock the SDK ``LabReport`` data-layer existence checks to pass by default."""
    with patch("canvas_sdk.effects.lab_report.base.LabReportModel.objects") as mock_report:
        mock_report.filter.return_value.exists.return_value = True
        yield {"report": mock_report}


@pytest.fixture
def valid_create_data() -> dict[str, Any]:
    """Valid kwargs for creating a decoupled lab report (no order, no values)."""
    return {
        "patient_id": "29cc62645764b7c4b16a2459",
        "external_id": "myplugin:ocr-2026-06-17-44",
        "report_name": "CBC scanned 2026-06-17",
        "date_performed": datetime.datetime(2026, 6, 17, 8, 15, 0),
    }


def test_create_real_round_trip(valid_create_data: dict[str, Any]) -> None:
    """create() produces a real Effect typed CREATE_LAB_REPORT with the full payload."""
    effect = LabReport(**valid_create_data).create()

    assert effect.type == EffectType.CREATE_LAB_REPORT
    payload = json.loads(effect.payload)
    assert payload["data"]["external_id"] == "myplugin:ocr-2026-06-17-44"
    assert payload["data"]["patient_id"] == "29cc62645764b7c4b16a2459"
    assert payload["data"]["report_name"] == "CBC scanned 2026-06-17"
    assert payload["data"]["date_performed"] == "2026-06-17T08:15:00"


@patch("canvas_sdk.effects.lab_report.base.Effect")
def test_create_emits_create_lab_report(
    mock_effect: MagicMock, valid_create_data: dict[str, Any]
) -> None:
    """create() emits an effect typed CREATE_LAB_REPORT."""
    LabReport(**valid_create_data).create()

    mock_effect.assert_called_once()
    assert mock_effect.call_args.kwargs["type"] == "CREATE_LAB_REPORT"


def test_create_requires_patient_id() -> None:
    """create() fails without patient_id."""
    with pytest.raises(ValidationError):
        LabReport(external_id="myplugin:ocr-44").create()


def test_create_requires_external_id() -> None:
    """create() fails without an external_id handle."""
    with pytest.raises(ValidationError):
        LabReport(patient_id="29cc62645764b7c4b16a2459").create()


def test_create_forbids_report_id(valid_create_data: dict[str, Any]) -> None:
    """create() fails when a Canvas report_id is supplied (creation assigns it)."""
    with pytest.raises(ValidationError):
        LabReport(report_id="canvas-uuid", **valid_create_data).create()


@patch("canvas_sdk.effects.lab_report.base.Effect")
def test_update_emits_update_lab_report(
    mock_effect: MagicMock, mock_db_queries: dict[str, MagicMock]
) -> None:
    """update() emits UPDATE_LAB_REPORT carrying only the dirty fields."""
    LabReport(external_id="myplugin:ocr-44", report_name="Complete Blood Count").update()

    assert mock_effect.call_args.kwargs["type"] == "UPDATE_LAB_REPORT"
    payload = json.loads(mock_effect.call_args.kwargs["payload"])
    assert payload["data"]["external_id"] == "myplugin:ocr-44"
    assert payload["data"]["report_name"] == "Complete Blood Count"
    assert "patient_id" not in payload["data"]


def test_update_requires_a_handle(mock_db_queries: dict[str, MagicMock]) -> None:
    """update() fails without report_id or external_id."""
    with pytest.raises(ValidationError):
        LabReport(report_name="x").update()


def test_update_requires_a_mutable_field(mock_db_queries: dict[str, MagicMock]) -> None:
    """update() fails when a handle is given but nothing to change."""
    with pytest.raises(ValidationError):
        LabReport(external_id="myplugin:ocr-44").update()


def test_update_nonexistent_report_raises(mock_db_queries: dict[str, MagicMock]) -> None:
    """update() fails when no report matches the handle."""
    mock_db_queries["report"].filter.return_value.exists.return_value = False
    with pytest.raises(ValidationError):
        LabReport(external_id="missing", report_name="x").update()


@patch("canvas_sdk.effects.lab_report.base.Effect")
def test_enter_in_error_emits_effect_with_external_id(
    mock_effect: MagicMock, mock_db_queries: dict[str, MagicMock]
) -> None:
    """enter_in_error() emits ENTER_IN_ERROR_LAB_REPORT with only the external_id handle."""
    LabReport(external_id="myplugin:ocr-44").enter_in_error()

    assert mock_effect.call_args.kwargs["type"] == "ENTER_IN_ERROR_LAB_REPORT"
    payload = json.loads(mock_effect.call_args.kwargs["payload"])
    assert payload == {"data": {"external_id": "myplugin:ocr-44"}}


@patch("canvas_sdk.effects.lab_report.base.Effect")
def test_enter_in_error_emits_effect_with_report_id(
    mock_effect: MagicMock, mock_db_queries: dict[str, MagicMock]
) -> None:
    """enter_in_error() supports the Canvas report_id handle."""
    LabReport(report_id="canvas-uuid").enter_in_error()

    payload = json.loads(mock_effect.call_args.kwargs["payload"])
    assert payload == {"data": {"report_id": "canvas-uuid"}}


def test_enter_in_error_requires_a_handle(mock_db_queries: dict[str, MagicMock]) -> None:
    """enter_in_error() fails without a handle."""
    with pytest.raises(ValidationError):
        LabReport().enter_in_error()


def test_enter_in_error_rejects_other_fields(mock_db_queries: dict[str, MagicMock]) -> None:
    """enter_in_error() fails when any non-handle field is set."""
    with pytest.raises(ValidationError):
        LabReport(external_id="myplugin:ocr-44", report_name="x").enter_in_error()
