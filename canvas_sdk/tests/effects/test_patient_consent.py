"""Tests for the RecordPatientConsent effect."""

import base64
import datetime
import json
from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.patient_consent import (
    ConsentCodingReference,
    ConsentDocument,
    RecordPatientConsent,
)
from canvas_sdk.v1.data.patient_consent import PatientConsentStatus

MODULE = "canvas_sdk.effects.patient_consent"


@pytest.fixture
def db() -> Iterator[dict[str, MagicMock]]:
    """Make the patient and both coding lookups report that the rows exist."""
    with (
        patch(f"{MODULE}.Patient.objects") as patient,
        patch(f"{MODULE}.PatientConsentCoding.objects") as coding,
        patch(f"{MODULE}.PatientConsentRejectionCoding.objects") as rejection,
    ):
        for mock in (patient, coding, rejection):
            mock.filter.return_value.exists.return_value = True
        yield {"patient": patient, "coding": coding, "rejection": rejection}


def _effect(**overrides: Any) -> RecordPatientConsent:
    """Build a valid acceptance, with any field replaced by the overrides."""
    fields: dict[str, Any] = {
        "patient_id": "a" * 32,
        "consent": ConsentCodingReference(system="INTERNAL", code="TELEHEALTH"),
        "state": PatientConsentStatus.ACCEPTED_VIA_PORTAL,
        "effective_date": datetime.date(2026, 10, 7),
    }
    return RecordPatientConsent(**(fields | overrides))


def test_apply_emits_the_payload(db: dict[str, MagicMock]) -> None:
    """The effect carries every field in the data envelope."""
    content = base64.b64encode(b"%PDF-1.4").decode()
    effect = _effect(document=ConsentDocument(filename="signed.pdf", content=content)).apply()

    assert effect.type == EffectType.RECORD_PATIENT_CONSENT
    assert json.loads(effect.payload) == {
        "data": {
            "patient_id": "a" * 32,
            "consent": {"system": "INTERNAL", "code": "TELEHEALTH", "display": ""},
            "state": "accepted_via_patient_portal",
            "effective_date": "2026-10-07",
            "rejection_reason": None,
            "document": {"filename": "signed.pdf", "content": content},
        }
    }


@pytest.mark.parametrize("missing", ["patient_id", "consent", "state", "effective_date"])
def test_required_fields(db: dict[str, MagicMock], missing: str) -> None:
    """Each required field missing raises a ValidationError that names it."""
    with pytest.raises(ValidationError, match=missing):
        _effect(**{missing: None}).apply()


def test_coding_reference_needs_code_or_display() -> None:
    """A reference with only a system cannot find a coding."""
    with pytest.raises(ValidationError, match="code or a display"):
        ConsentCodingReference(system="INTERNAL")


def test_rejection_with_reason(db: dict[str, MagicMock]) -> None:
    """A rejected state carries its reason into the payload."""
    reason = ConsentCodingReference(system="INTERNAL", display="Patient declined")
    payload = json.loads(
        _effect(state=PatientConsentStatus.REJECTED, rejection_reason=reason).apply().payload
    )

    assert payload["data"]["rejection_reason"] == {
        "system": "INTERNAL",
        "code": "",
        "display": "Patient declined",
    }


@pytest.mark.parametrize(
    "state", [PatientConsentStatus.ACCEPTED, PatientConsentStatus.ACCEPTED_VIA_PORTAL]
)
def test_rejection_reason_with_accepted_state_is_rejected(
    db: dict[str, MagicMock], state: PatientConsentStatus
) -> None:
    """An accepted consent cannot carry a rejection reason."""
    reason = ConsentCodingReference(system="INTERNAL", code="R1")
    with pytest.raises(ValidationError, match="only with a rejected state"):
        _effect(state=state, rejection_reason=reason).apply()


def test_document_content_must_be_base64(db: dict[str, MagicMock]) -> None:
    """Content that does not decode as base64 fails at apply()."""
    with pytest.raises(ValidationError, match="base64"):
        _effect(document=ConsentDocument(filename="x.pdf", content="not base64!")).apply()


def test_document_filename_is_required() -> None:
    """An empty filename fails when the document is built."""
    with pytest.raises(ValidationError):
        ConsentDocument(filename="", content="")


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("patient", "Patient"),
        ("coding", "consent coding"),
        ("rejection", "rejection coding"),
    ],
)
def test_unknown_references_are_rejected(db: dict[str, MagicMock], key: str, message: str) -> None:
    """A patient or coding that does not exist fails at apply()."""
    db[key].filter.return_value.exists.return_value = False
    reason = ConsentCodingReference(system="INTERNAL", code="R1")

    with pytest.raises(ValidationError, match=message):
        _effect(state=PatientConsentStatus.REJECTED, rejection_reason=reason).apply()


def test_coding_lookup_uses_code_before_display(db: dict[str, MagicMock]) -> None:
    """The coding lookup matches the interpreter: code and system when a code is present."""
    _effect(consent=ConsentCodingReference(system="INTERNAL", code="C1", display="Ignored")).apply()

    db["coding"].filter.assert_called_with(system="INTERNAL", code="C1")


@pytest.mark.parametrize("filename", ["../x.pdf", "a/b.pdf", "a\\b.pdf", "x" * 252 + ".pdf"])
def test_document_filename_must_be_a_plain_name(filename: str) -> None:
    """A filename with a path component, or longer than the file field allows, fails when built."""
    with pytest.raises(ValidationError):
        ConsentDocument(filename=filename, content=base64.b64encode(b"%PDF").decode())


def test_document_content_is_required() -> None:
    """Empty content fails when the document is built, so no empty proof is filed."""
    with pytest.raises(ValidationError):
        ConsentDocument(filename="x.pdf", content="")
