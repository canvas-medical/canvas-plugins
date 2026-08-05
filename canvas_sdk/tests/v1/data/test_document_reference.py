from unittest.mock import patch

import pytest

from canvas_sdk.test_utils.factories import ContentTypeFactory, ImagingReportFactory
from canvas_sdk.v1.data.document_reference import DocumentReference
from canvas_sdk.v1.data.imaging import ImagingReport


def test_document_url_with_document() -> None:
    """document_url returns a presigned URL when document is set."""
    doc_ref = DocumentReference()
    doc_ref.document = "some/key.pdf"
    doc_ref.document_absolute_url = "https://example.com/fallback.pdf"

    with patch(
        "canvas_sdk.v1.data.document_reference.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert doc_ref.document_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("some/key.pdf")


def test_document_url_falls_back_to_absolute_url() -> None:
    """document_url returns document_absolute_url when document is empty."""
    doc_ref = DocumentReference()
    doc_ref.document = ""
    doc_ref.document_absolute_url = "https://example.com/fallback.pdf"

    assert doc_ref.document_url == "https://example.com/fallback.pdf"


def test_document_url_returns_none_when_both_empty() -> None:
    """document_url returns None when both document and document_absolute_url are empty."""
    doc_ref = DocumentReference()
    doc_ref.document = ""
    doc_ref.document_absolute_url = None

    assert doc_ref.document_url is None


def test_document_reference_str() -> None:
    """__str__ returns a readable representation."""
    doc_ref = DocumentReference()
    doc_ref.id = "abc123"

    assert str(doc_ref) == "DocumentReference(id=abc123)"


@pytest.mark.django_db
def test_related_object_resolves_to_sdk_model() -> None:
    """related_object resolves content_type + object_id to the SDK model instance."""
    report = ImagingReportFactory.create()
    content_type = ContentTypeFactory.create(app_label="api", model="imagingreport")

    doc_ref = DocumentReference()
    doc_ref.content_type = content_type
    doc_ref.object_id = report.dbid

    resolved = doc_ref.related_object

    assert isinstance(resolved, ImagingReport)
    assert resolved.dbid == report.dbid


@pytest.mark.django_db
def test_related_object_none_for_unmapped_content_type() -> None:
    """related_object returns None when the content type has no SDK equivalent."""
    content_type = ContentTypeFactory.create(app_label="api", model="note")

    doc_ref = DocumentReference()
    doc_ref.content_type = content_type
    doc_ref.object_id = 123

    assert doc_ref.related_object is None


def test_related_object_none_without_content_type() -> None:
    """related_object returns None when there is no related object."""
    doc_ref = DocumentReference()
    doc_ref.object_id = None

    assert doc_ref.related_object is None
