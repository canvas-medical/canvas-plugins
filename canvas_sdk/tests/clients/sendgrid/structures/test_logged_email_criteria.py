from datetime import UTC, datetime

import pytest

from canvas_sdk.clients.sendgrid.constants.criterion_operation import CriterionOperation
from canvas_sdk.clients.sendgrid.constants.status_email import StatusEmail
from canvas_sdk.clients.sendgrid.structures.criterion_datetime import CriterionDatetime
from canvas_sdk.clients.sendgrid.structures.logged_email_criteria import LoggedEmailCriteria
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test LoggedEmailCriteria dataclass has correct field types."""
    tested = LoggedEmailCriteria
    fields = {
        "message_id": str,
        "subject": str,
        "to_email": str,
        "reason": str,
        "status": list[StatusEmail],
        "message_created_at": list[CriterionDatetime],
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("criteria", "expected"),
    [
        pytest.param(
            LoggedEmailCriteria(
                message_id="MSG123",
                subject="",
                to_email="test@example.com",
                reason="",
                status=[],
                message_created_at=[],
            ),
            'sg_message_id="MSG123" AND to_email="test@example.com"',
            id="basic_criteria",
        ),
        pytest.param(
            LoggedEmailCriteria(
                message_id="",
                subject="Test Subject",
                to_email="user@example.com",
                reason="bounce",
                status=[StatusEmail.BOUNCED, StatusEmail.DROPPED],
                message_created_at=[],
            ),
            'subject="Test Subject" '
            'AND to_email="user@example.com" '
            'AND reason="bounce" '
            "AND status IN ('bounced','dropped')",
            id="with_status",
        ),
        pytest.param(
            LoggedEmailCriteria(
                message_id="",
                subject="",
                to_email="user@example.com",
                reason="",
                status=[StatusEmail.DELIVERED],
                message_created_at=[
                    CriterionDatetime(
                        date_time=datetime(2025, 12, 15, 10, 0, 0, tzinfo=UTC),
                        operation=CriterionOperation.GREATER_THAN,
                    ),
                    CriterionDatetime(
                        date_time=datetime(2025, 12, 16, 10, 0, 0, tzinfo=UTC),
                        operation=CriterionOperation.LOWER_THAN,
                    ),
                ],
            ),
            'to_email="user@example.com" '
            "AND status IN ('delivered') "
            'AND sg_message_id_created_at > TIMESTAMP "2025-12-15T10:00:00Z" '
            'AND sg_message_id_created_at < TIMESTAMP "2025-12-16T10:00:00Z"',
            id="with_datetime_range",
        ),
    ],
)
def test_to_str(criteria: LoggedEmailCriteria, expected: str) -> None:
    """Test LoggedEmailCriteria.to_str converts instance to query string."""
    result = criteria.to_str()
    assert result == expected
