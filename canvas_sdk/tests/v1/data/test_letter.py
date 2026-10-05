from unittest.mock import patch

import pytest

from canvas_sdk.test_utils.factories import LetterFactory
from canvas_sdk.v1.data.letter import Letter


def test_printed_document_url_with_document() -> None:
    """printed_document_url returns a presigned URL when a printed document is set."""
    letter = Letter()
    letter.printed_document = "printed_attachments_letter_12"

    with patch(
        "canvas_sdk.v1.data.letter.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert letter.printed_document_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("printed_attachments_letter_12")


@pytest.mark.parametrize("value", [None, ""])
def test_printed_document_url_returns_none_when_unset(value: str | None) -> None:
    """printed_document_url returns None when no printed document is set."""
    letter = Letter()
    letter.printed_document = value

    assert letter.printed_document_url is None


@pytest.mark.django_db
def test_printed_document_round_trips() -> None:
    """The printed document's S3 key is readable through the data model."""
    letter = LetterFactory.create(printed_document="printed_attachments_letter_12")

    fetched = Letter.objects.get(dbid=letter.dbid)

    assert fetched.printed_document.name == "printed_attachments_letter_12"
