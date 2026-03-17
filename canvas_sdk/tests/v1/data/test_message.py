from unittest.mock import patch

from canvas_sdk.v1.data.message import MessageAttachment


def test_file_url_with_file() -> None:
    """file_url returns a presigned URL when file is set."""
    attachment = MessageAttachment()
    attachment.file = "attachments/doc.pdf"

    with patch(
        "canvas_sdk.v1.data.message.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert attachment.file_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("attachments/doc.pdf")


def test_file_url_without_file() -> None:
    """file_url returns None when file is empty."""
    attachment = MessageAttachment()
    attachment.file = ""

    assert attachment.file_url is None
