from unittest.mock import patch

import pytest

from canvas_sdk.test_utils.factories import PatientAdministrativeDocumentFactory
from canvas_sdk.v1.data.patient_administrative_document import PatientAdministrativeDocument


def test_document_url_with_document() -> None:
    """document_url returns a presigned URL when a document is set."""
    pad = PatientAdministrativeDocument()
    pad.document = "administrative/doc.pdf"

    with patch(
        "canvas_sdk.v1.data.patient_administrative_document.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert pad.document_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("administrative/doc.pdf")


def test_document_url_returns_none_when_no_document() -> None:
    """document_url returns None when no document is set."""
    pad = PatientAdministrativeDocument()
    pad.document = ""

    assert pad.document_url is None


@pytest.mark.django_db
def test_fields_round_trip() -> None:
    """PAD fields are readable through the data model."""
    pad = PatientAdministrativeDocumentFactory.create(
        name="Insurance card",
        review_mode="IN",
        comment="front and back",
    )

    fetched = PatientAdministrativeDocument.objects.get(dbid=pad.dbid)

    assert fetched.name == "Insurance card"
    assert fetched.review_mode == "IN"
    assert fetched.comment == "front and back"
    assert fetched.patient_id == pad.patient_id
    assert fetched.document.name == "administrative/doc.pdf"
