from dataclasses import dataclass
from datetime import datetime

from canvas_sdk.clients.sendgrid.constants.constants import Constants
from canvas_sdk.clients.sendgrid.constants.criterion_operation import CriterionOperation


@dataclass(frozen=True)
class CriterionDatetime:
    """Represents a datetime comparison criterion for SendGrid queries.

    https://www.twilio.com/docs/sendgrid/api-reference/email-logs/filter-all-messages
    """

    date_time: datetime
    operation: CriterionOperation

    def to_str(self) -> str:
        """Convert datetime criterion to query string format."""
        operation = self.operation.value
        timestamp = self.date_time.strftime(Constants.rfc3339_format)
        return f'sg_message_id_created_at {operation} TIMESTAMP "{timestamp}"'


__exports__ = ()
