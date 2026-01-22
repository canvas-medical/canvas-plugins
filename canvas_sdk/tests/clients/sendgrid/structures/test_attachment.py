from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest

from canvas_sdk.clients.sendgrid.constants.attachment_disposition import AttachmentDisposition
from canvas_sdk.clients.sendgrid.structures.attachment import Attachment
from canvas_sdk.clients.sendgrid.structures.request_failed import RequestFailed
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test Attachment dataclass has correct field types."""
    tested = Attachment
    fields = {
        "content_id": "str",
        "content": "str",
        "type": "str",
        "filename": "str",
        "disposition": "AttachmentDisposition",
    }
    result = is_dataclass(tested, fields)
    expected = True
    assert result is expected


@pytest.mark.parametrize(
    ("attachment", "expected"),
    [
        pytest.param(
            Attachment(
                content_id="img123",
                content="aGVsbG8gd29ybGQ=",
                type="image/png",
                filename="test.png",
                disposition=AttachmentDisposition.INLINE,
            ),
            {
                "content_id": "img123",
                "content": "aGVsbG8gd29ybGQ=",
                "type": "image/png",
                "filename": "test.png",
                "disposition": "inline",
            },
            id="inline_attachment",
        ),
        pytest.param(
            Attachment(
                content_id="",
                content="ZG9jdW1lbnQgY29udGVudA==",
                type="application/pdf",
                filename="document.pdf",
                disposition=AttachmentDisposition.ATTACHMENT,
            ),
            {
                "content_id": "",
                "content": "ZG9jdW1lbnQgY29udGVudA==",
                "type": "application/pdf",
                "filename": "document.pdf",
                "disposition": "attachment",
            },
            id="regular_attachment",
        ),
    ],
)
def test_to_dict(attachment: Attachment, expected: dict) -> None:
    """Test Attachment.to_dict converts instance to dictionary."""
    result = attachment.to_dict()
    assert result == expected


def test_from_url_inline__with_content_id() -> None:
    """Test Attachment.from_url_inline creates inline attachment when content_id provided."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.content = b"image data"
    mock_response.headers = {"Content-Type": "image/png"}

    mock_http = MagicMock()
    mock_http.get.side_effect = [mock_response]

    mock_http_class = MagicMock(side_effect=[mock_http])
    with patch("canvas_sdk.clients.sendgrid.structures.attachment.Http", mock_http_class):
        result = Attachment.from_url_inline(
            "https://example.com/image.png",
            {"Authorization": "Bearer token"},
            "test.png",
            "img123",
        )

    expected = Attachment(
        content_id="img123",
        content="aW1hZ2UgZGF0YQ==",
        type="image/png",
        filename="test.png",
        disposition=AttachmentDisposition.INLINE,
    )
    assert result == expected

    exp_calls = [call("https://example.com/image.png")]
    assert mock_http_class.mock_calls == exp_calls

    exp_calls = [call("", headers={"Authorization": "Bearer token"})]
    assert mock_http.get.mock_calls == exp_calls


def test_from_url_inline__without_content_id() -> None:
    """Test Attachment.from_url_inline creates regular attachment when content_id is empty."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.content = b"pdf content"
    mock_response.headers = {"Content-Type": "application/pdf"}

    mock_http = MagicMock()
    mock_http.get.side_effect = [mock_response]

    mock_http_class = MagicMock(side_effect=[mock_http])
    with patch("canvas_sdk.clients.sendgrid.structures.attachment.Http", mock_http_class):
        result = Attachment.from_url_inline(
            "https://example.com/doc.pdf",
            {"Authorization": "Bearer token"},
            "document.pdf",
            "",
        )

    expected = Attachment(
        content_id="",
        content="cGRmIGNvbnRlbnQ=",
        type="application/pdf",
        filename="document.pdf",
        disposition=AttachmentDisposition.ATTACHMENT,
    )
    assert result == expected

    exp_calls = [call("https://example.com/doc.pdf")]
    assert mock_http_class.mock_calls == exp_calls

    exp_calls = [call("", headers={"Authorization": "Bearer token"})]
    assert mock_http.get.mock_calls == exp_calls


def test_from_url_inline__raises_request_failed() -> None:
    """Test Attachment.from_url_inline raises RequestFailed on HTTP error."""
    mock_response = SimpleNamespace(
        status_code=HTTPStatus.NOT_FOUND,
        content=b"File not found",
    )

    mock_http = MagicMock()
    mock_http.get.side_effect = [mock_response]

    mock_http_class = MagicMock(side_effect=[mock_http])
    with (
        patch("canvas_sdk.clients.sendgrid.structures.attachment.Http", mock_http_class),
        pytest.raises(RequestFailed) as exc_info,
    ):
        Attachment.from_url_inline(
            "https://example.com/missing.png",
            {"Authorization": "Bearer token"},
            "missing.png",
            "img999",
        )

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.message == "File not found"

    exp_calls = [call("https://example.com/missing.png")]
    assert mock_http_class.mock_calls == exp_calls

    exp_calls = [call("", headers={"Authorization": "Bearer token"})]
    assert mock_http.get.mock_calls == exp_calls


def test_from_url() -> None:
    """Test Attachment.from_url calls from_url_inline with empty content_id."""
    mock_attachment = Attachment(
        content_id="",
        content="ZmlsZSBjb250ZW50",
        type="text/plain",
        filename="file.txt",
        disposition=AttachmentDisposition.ATTACHMENT,
    )

    mock_from_url_inline = MagicMock(side_effect=[mock_attachment])
    with patch.object(Attachment, "from_url_inline", mock_from_url_inline):
        result = Attachment.from_url(
            "https://example.com/file.txt",
            {"Authorization": "Bearer token"},
            "file.txt",
        )

    assert result == mock_attachment

    exp_calls = [
        call(
            "https://example.com/file.txt",
            {"Authorization": "Bearer token"},
            "file.txt",
            "",
        )
    ]
    assert mock_from_url_inline.mock_calls == exp_calls
