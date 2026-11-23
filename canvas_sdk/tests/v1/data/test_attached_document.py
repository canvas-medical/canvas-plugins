"""Tests for the documents attached to letters and referrals."""

import pytest

from canvas_sdk.test_utils.factories import (
    ContentTypeFactory,
    LetterDocumentFactory,
    LetterFactory,
    PatientChartDocumentFactory,
    ReferralDocumentFactory,
    ReferralFactory,
)
from canvas_sdk.v1.data import (
    Letter,
    LetterDocument,
    PatientChartDocument,
    Referral,
    ReferralDocument,
)


@pytest.mark.django_db
def test_letter_documents_resolve_their_attached_object() -> None:
    """letter.documents lists a letter's attachments, each resolving to what it attaches."""
    letter = LetterFactory.create()
    chart_page = PatientChartDocumentFactory.create(name="Problem list")
    attachment = LetterDocumentFactory.create(
        letter=letter,
        label="Problem list",
        category="chart",
        content_type=ContentTypeFactory.create(model="patientchartdocument"),
        object_id=chart_page.dbid,
    )
    LetterDocumentFactory.create()

    documents = list(Letter.objects.get(id=letter.id).documents.all())

    assert documents == [attachment]
    assert documents[0].category == "chart"
    resolved = documents[0].related_object
    assert isinstance(resolved, PatientChartDocument)
    assert resolved.dbid == chart_page.dbid


@pytest.mark.django_db
def test_letter_document_with_unmapped_content_type_resolves_to_none() -> None:
    """related_object is None when the attachment's content type has no SDK model."""
    attachment = LetterDocumentFactory.create(content_type=ContentTypeFactory.create(model="x"))

    assert LetterDocument.objects.get(dbid=attachment.dbid).related_object is None


@pytest.mark.django_db
def test_referral_documents_list_a_referrals_attachments() -> None:
    """referral.documents lists a referral's attachments with their type, id and S3 location."""
    referral = ReferralFactory.create()
    uploaded = ReferralDocumentFactory.create(
        referral=referral,
        document_type="UPLOADED",
        document_id=None,
        url="referrals/fax.pdf",
        bucket="media-bucket",
    )
    report = ReferralDocumentFactory.create(referral=referral, document_id=42)
    ReferralDocumentFactory.create()

    documents = Referral.objects.get(id=referral.id).documents.order_by("dbid")

    assert list(documents) == [uploaded, report]
    assert (documents[0].url, documents[0].bucket, documents[0].document_id) == (
        "referrals/fax.pdf",
        "media-bucket",
        None,
    )
    assert (documents[1].document_type, documents[1].document_id) == ("LAB REPORT", 42)
    assert ReferralDocument.objects.filter(referral__patient=referral.patient).count() == 2


@pytest.mark.django_db
def test_patient_chart_documents_filter_by_active() -> None:
    """Chart pages carry their name, url template and active flag."""
    active = PatientChartDocumentFactory.create(
        name="Integrated care plan", url="api/CarePlan/{key}.html"
    )
    PatientChartDocumentFactory.create(is_active=False)

    pages = list(PatientChartDocument.objects.filter(is_active=True))

    assert pages == [active]
    assert (pages[0].name, pages[0].url) == ("Integrated care plan", "api/CarePlan/{key}.html")
