import datetime
from unittest.mock import patch

import pytest

from canvas_sdk.test_utils.factories import CanvasUserFactory, ContentTypeFactory, PatientFactory
from canvas_sdk.test_utils.factories.patient_administrative_document import (
    PatientAdministrativeDocumentFactory,
)
from canvas_sdk.v1.data.document_reference import DocumentReference, DocumentReferenceCoding
from canvas_sdk.v1.data.patient_consent import (
    PatientConsent,
    PatientConsentCoding,
    PatientConsentStatus,
)


def test_patient_consent_coding_has_document_field() -> None:
    """PatientConsentCoding.document exposes the consent template file."""
    coding = PatientConsentCoding()
    coding.document = "consents/my-consent.pdf"

    assert coding.document == "consents/my-consent.pdf"


def test_patient_consent_coding_document_is_nullable() -> None:
    """PatientConsentCoding.document can be None when no document is uploaded."""
    coding = PatientConsentCoding()

    assert not coding.document
    assert coding.document.name is None


def test_document_url_with_document() -> None:
    """document_url returns a presigned URL when document is set."""
    coding = PatientConsentCoding()
    coding.document = "consents/my-consent.pdf"

    with patch(
        "canvas_sdk.v1.data.patient_consent.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert coding.document_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("consents/my-consent.pdf")
        called_arg = mock.call_args.args[0]
        assert type(called_arg) is str


def test_document_url_returns_none_when_no_document() -> None:
    """document_url returns None when document is not set."""
    coding = PatientConsentCoding()
    coding.document = ""

    assert coding.document_url is None


def _make_consent() -> PatientConsent:
    category = PatientConsentCoding.objects.create(
        system="http://loinc.org",
        code="59284-0",
        display="Consent",
        user_selected=False,
        expiration_rule="never",
        is_mandatory=False,
        is_proof_required=False,
        show_in_patient_portal=False,
        summary="",
    )
    return PatientConsent.objects.create(
        patient=PatientFactory.create(),
        category=category,
        state=PatientConsentStatus.ACCEPTED,
        effective_date=datetime.date(2026, 1, 1),
        expired_date=datetime.date(2027, 1, 1),
        originator=CanvasUserFactory.create(),
    )


@pytest.mark.django_db
def test_documents_m2m_returns_signed_documents() -> None:
    """A consent exposes its signed administrative documents via the documents relation."""
    consent = _make_consent()
    doc_one = PatientAdministrativeDocumentFactory.create()
    doc_two = PatientAdministrativeDocumentFactory.create()
    consent.documents.add(doc_one, doc_two)

    assert set(consent.documents.values_list("dbid", flat=True)) == {doc_one.dbid, doc_two.dbid}


@pytest.mark.django_db
def test_active_document_is_latest_non_junked_by_original_date() -> None:
    """active_document returns the most recent non-junked signed document."""
    consent = _make_consent()
    older = PatientAdministrativeDocumentFactory.create(original_date=datetime.date(2026, 1, 1))
    newer = PatientAdministrativeDocumentFactory.create(original_date=datetime.date(2026, 6, 1))
    junked = PatientAdministrativeDocumentFactory.create(
        original_date=datetime.date(2026, 12, 1), junked=True
    )
    consent.documents.add(older, newer, junked)

    assert consent.active_document is not None
    assert consent.active_document.dbid == newer.dbid


@pytest.mark.django_db
def test_document_references_reaches_the_signed_documents_document_reference() -> None:
    """document_references resolves to the DocumentReference for a consent's signed document."""
    consent = _make_consent()
    doc = PatientAdministrativeDocumentFactory.create()
    consent.documents.add(doc)

    content_type = ContentTypeFactory.create(app_label="api", model="patientadministrativedocument")
    coding = DocumentReferenceCoding.objects.create(
        system="http://loinc.org", code="59284-0", display="Consent", user_selected=False
    )
    doc_ref = DocumentReference.objects.create(
        type=coding,
        date=datetime.date(2026, 6, 1),
        document_content_type="application/pdf",
        content_type=content_type,
        object_id=doc.dbid,
    )

    references = consent.document_references
    assert list(references.values_list("dbid", flat=True)) == [doc_ref.dbid]
    assert references.first().related_object.dbid == doc.dbid
