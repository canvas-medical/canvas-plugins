from datetime import UTC, datetime

import pytest

from canvas_sdk.clients.sendgrid.constants.criterion_operation import CriterionOperation
from canvas_sdk.clients.sendgrid.structures.criterion_datetime import CriterionDatetime
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test CriterionDatetime dataclass has correct field types."""
    tested = CriterionDatetime
    fields = {
        "date_time": datetime,
        "operation": CriterionOperation,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("criterion", "expected"),
    [
        pytest.param(
            CriterionDatetime(
                date_time=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
                operation=CriterionOperation.GREATER_THAN,
            ),
            'sg_message_id_created_at > TIMESTAMP "2025-12-15T10:30:00Z"',
            id="greater_than",
        ),
        pytest.param(
            CriterionDatetime(
                date_time=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
                operation=CriterionOperation.LOWER_THAN_OR_EQUAL,
            ),
            'sg_message_id_created_at <= TIMESTAMP "2025-12-16T14:20:00Z"',
            id="lower_than_or_equal",
        ),
        pytest.param(
            CriterionDatetime(
                date_time=datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC),
                operation=CriterionOperation.EQUAL,
            ),
            'sg_message_id_created_at = TIMESTAMP "2025-01-01T00:00:00Z"',
            id="equal",
        ),
    ],
)
def test_to_str(criterion: CriterionDatetime, expected: str) -> None:
    """Test CriterionDatetime.to_str converts instance to query string."""
    result = criterion.to_str()
    assert result == expected
