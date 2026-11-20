"""Tests for the DocumentAnnotation model."""

from unittest.mock import patch

import pytest

from canvas_sdk.test_utils.factories import (
    ContentTypeFactory,
    DocumentAnnotationFactory,
    IntegrationTaskFactory,
    LabReportFactory,
    StaffFactory,
    UncategorizedClinicalDocumentFactory,
)
from canvas_sdk.v1.data import DocumentAnnotation, LabReport, UncategorizedClinicalDocument


@pytest.mark.django_db
def test_signers_and_creator_resolve_both_ways() -> None:
    """An annotation's signers and creator resolve, and each staff member reaches it back."""
    creator = StaffFactory.create()
    signer = StaffFactory.create()
    annotation = DocumentAnnotationFactory.create(created_by=creator)
    annotation.signers.add(signer)
    DocumentAnnotationFactory.create()

    fetched = DocumentAnnotation.objects.get(id=annotation.id)

    assert fetched.created_by == creator
    assert list(fetched.signers.all()) == [signer]
    assert list(creator.document_annotations.all()) == [fetched]
    assert list(signer.signed_document_annotations.all()) == [fetched]


@pytest.mark.django_db
def test_annotation_before_filing_links_to_its_integration_task() -> None:
    """An annotation made on an unfiled document is reached from its integration task."""
    task = IntegrationTaskFactory.create()
    annotation = DocumentAnnotationFactory.create(
        integration_task=task, content_type=None, object_id=None
    )

    assert list(task.document_annotations.all()) == [annotation]
    assert DocumentAnnotation.objects.get(id=annotation.id).related_object is None


@pytest.mark.django_db
def test_related_object_resolves_the_annotated_document() -> None:
    """related_object resolves content_type + object_id to the annotated report or document."""
    document = UncategorizedClinicalDocumentFactory.create()
    report = LabReportFactory.create()
    on_document = DocumentAnnotationFactory.create(object_id=document.dbid)
    on_report = DocumentAnnotationFactory.create(
        content_type=ContentTypeFactory.create(model="labreport"), object_id=report.dbid
    )

    resolved_document = DocumentAnnotation.objects.get(id=on_document.id).related_object
    resolved_report = DocumentAnnotation.objects.get(id=on_report.id).related_object

    assert isinstance(resolved_document, UncategorizedClinicalDocument)
    assert resolved_document.dbid == document.dbid
    assert isinstance(resolved_report, LabReport)
    assert resolved_report.dbid == report.dbid


@pytest.mark.django_db
def test_document_url_presigns_the_annotated_pdf() -> None:
    """document_url presigns the annotated file's key."""
    annotation = DocumentAnnotationFactory.create(document="document_annotations/signed.pdf")

    with patch(
        "canvas_sdk.v1.data.document_annotation.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as presign:
        assert annotation.document_url == "https://s3.example.com/presigned"

    presign.assert_called_once_with("document_annotations/signed.pdf")
