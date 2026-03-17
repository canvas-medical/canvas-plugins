from unittest.mock import patch

from canvas_sdk.v1.data.document_reference import DocumentReference


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
