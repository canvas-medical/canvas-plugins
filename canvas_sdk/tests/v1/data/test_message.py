from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from canvas_sdk.v1.data.message import MessageAttachment, MessageTransmission


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


@pytest.mark.django_db
def test_transmission_delivered_and_failed_are_timestamps() -> None:
    """Transmission delivered/failed read back as the timestamps home-app stores, or None."""
    delivered_at = datetime(2026, 9, 1, 12, 30, tzinfo=UTC)
    transmission = MessageTransmission.objects.create(delivered=delivered_at)

    transmission.refresh_from_db()

    assert transmission.delivered == delivered_at
    assert transmission.failed is None
    assert list(MessageTransmission.objects.filter(failed__isnull=True)) == [transmission]
