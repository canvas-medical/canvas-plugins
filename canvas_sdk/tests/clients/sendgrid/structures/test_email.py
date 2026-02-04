from datetime import UTC, datetime
from unittest.mock import call, patch

import pytest

from canvas_sdk.clients.sendgrid.structures.address import Address
from canvas_sdk.clients.sendgrid.structures.attachment import Attachment
from canvas_sdk.clients.sendgrid.structures.body_content import BodyContent
from canvas_sdk.clients.sendgrid.structures.email import Email
from canvas_sdk.clients.sendgrid.structures.recipient import Recipient
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test Email dataclass has correct field types."""
    tested = Email
    fields = {
        "sender": Address,
        "reply_tos": list[Address],
        "recipients": list[Recipient],
        "subject": str,
        "bodies": list[BodyContent],
        "attachments": list[Attachment],
        "send_at": int,
    }
    assert is_dataclass(tested, fields)


def test_now() -> None:
    """Test Email.now calls datetime.now with UTC and returns timestamp."""
    mock_dt = datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC)

    with patch("canvas_sdk.clients.sendgrid.structures.email.datetime") as mock_datetime:
        mock_datetime.now.side_effect = [mock_dt]
        mock_datetime.UTC = UTC
        result = Email.now()

    assert result == 1765794600

    exp_calls = [call(tz=UTC)]
    assert mock_datetime.now.mock_calls == exp_calls


@pytest.mark.parametrize(
    ("dt", "expected"),
    [
        pytest.param(
            datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
            1765794600,
            id="specific_datetime",
        ),
        pytest.param(
            datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC),
            1735689600,
            id="new_year",
        ),
    ],
)
def test_timestamp(dt: datetime, expected: int) -> None:
    """Test Email.timestamp converts datetime to unix timestamp."""
    result = Email.timestamp(dt)
    assert result == expected
