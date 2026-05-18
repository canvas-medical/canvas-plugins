"""Round-trip tests for the HealthGorilla lab ingest effects.

These pin the wire shape — proto enum value, payload key set, and key
serialization — so the home-app interpreters that read these effects
have a stable contract to consume.
"""

import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.lab_order import (
    HealthGorillaLabOrderIngest,
    HealthGorillaLabReportIngest,
)
from canvas_sdk.effects.lab_order.health_gorilla_ingest import _LabValueIn


def test_lab_order_ingest_emits_effect_with_full_payload() -> None:
    """All required fields and optionals appear in the effect payload."""
    effect = HealthGorillaLabOrderIngest(
        patient_id="29cc62645764b7c4b16a2459",
        ordering_provider_npi="1598705535",
        note_id="note-uuid-1",
        ontology_lab_partner="Quest Diagnostics",
        date_ordered=datetime(2026, 4, 2, 21, 29, 6, tzinfo=UTC),
        hg_request_result=(
            "https://api.healthgorilla.com/fhir/RequestGroup/71dfce69e4397f5cac7adfac"
        ),
        test_codes=["10231", "496", "561"],
        external_id="71dfce69e4397f5cac7adfac",
        comment="standing order",
    )

    proto_effect = effect.apply()

    assert proto_effect.type == EffectType.HEALTH_GORILLA_LAB_ORDER_INGEST
    assert json.loads(proto_effect.payload) == {
        "data": {
            "patient_id": "29cc62645764b7c4b16a2459",
            "ordering_provider_npi": "1598705535",
            "note_id": "note-uuid-1",
            "ontology_lab_partner": "Quest Diagnostics",
            "date_ordered": "2026-04-02T21:29:06+00:00",
            "hg_request_result": (
                "https://api.healthgorilla.com/fhir/RequestGroup/71dfce69e4397f5cac7adfac"
            ),
            "test_codes": ["10231", "496", "561"],
            "external_id": "71dfce69e4397f5cac7adfac",
            "comment": "standing order",
        }
    }


def test_lab_order_ingest_requires_hg_request_result() -> None:
    """The skip-send marker is required — without it, Canvas's send-to-HG
    worker would pick the order up and try to forward to HG.
    """
    with pytest.raises(ValidationError):
        HealthGorillaLabOrderIngest(
            patient_id="p",
            ordering_provider_npi="1598705535",
            note_id="n",
            ontology_lab_partner="QUEST",
            date_ordered=datetime(2026, 4, 2, tzinfo=UTC),
            test_codes=["10231"],
            # hg_request_result missing
        )  # type: ignore[call-arg]


def test_lab_report_ingest_emits_effect_with_pdf_url() -> None:
    """The PDF can be supplied as a URL the home-app interpreter fetches."""
    effect = HealthGorillaLabReportIngest(
        lab_order_id="ord-uuid-1",
        patient_id="29cc62645764b7c4b16a2459",
        external_id="report-id-1",
        version=1,
        date_performed=datetime(2026, 4, 3, 8, 15, tzinfo=UTC),
        lab_values=[
            _LabValueIn(
                ontology_test_code="718-7",
                ontology_test_name="Hemoglobin",
                value="14.2",
                units="g/dL",
                reference_range="13.5-17.5",
            ),
        ],
        pdf_url="https://partner-bucket.example.com/report.pdf",
    )

    proto_effect = effect.apply()

    assert proto_effect.type == EffectType.HEALTH_GORILLA_LAB_REPORT_INGEST
    payload = json.loads(proto_effect.payload)
    assert payload["data"]["lab_order_id"] == "ord-uuid-1"
    assert payload["data"]["external_id"] == "report-id-1"
    assert payload["data"]["version"] == 1
    assert payload["data"]["pdf_url"] == "https://partner-bucket.example.com/report.pdf"
    assert payload["data"]["pdf_base64"] == ""
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


def test_lab_report_ingest_rejects_version_zero() -> None:
    """Version is 1-indexed; version=0 is invalid (matches LabReport contract)."""
    with pytest.raises(ValidationError):
        HealthGorillaLabReportIngest(
            lab_order_id="ord",
            patient_id="p",
            external_id="r",
            version=0,
            date_performed=datetime(2026, 4, 3, tzinfo=UTC),
            lab_values=[],
        )


def test_lab_report_ingest_inline_pdf_base64() -> None:
    """Small PDFs can be passed inline as base64; URL stays empty."""
    effect = HealthGorillaLabReportIngest(
        lab_order_id="ord-uuid-1",
        patient_id="p",
        external_id="r",
        version=1,
        date_performed=datetime(2026, 4, 3, tzinfo=UTC),
        lab_values=[],
        pdf_base64="JVBERi0xLjQKJeLjz9MK",
    )

    payload = json.loads(effect.apply().payload)
    assert payload["data"]["pdf_base64"] == "JVBERi0xLjQKJeLjz9MK"
    assert payload["data"]["pdf_url"] == ""
