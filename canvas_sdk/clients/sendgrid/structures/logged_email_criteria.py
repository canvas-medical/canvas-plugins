from dataclasses import dataclass

from canvas_sdk.clients.sendgrid.constants.status_email import StatusEmail
from canvas_sdk.clients.sendgrid.structures.criterion_datetime import CriterionDatetime


@dataclass(frozen=True)
class LoggedEmailCriteria:
    """Represents search criteria for querying logged emails.

    https://www.twilio.com/docs/sendgrid/api-reference/email-logs/filter-all-messages
    """

    message_id: str
    subject: str
    to_email: str
    reason: str
    status: list[StatusEmail]
    message_created_at: list[CriterionDatetime]

    def to_str(self) -> str:
        """Convert criteria to SendGrid query string format."""
        result: list[str] = []
        equals = {
            "sg_message_id": self.message_id,
            "subject": self.subject,
            "to_email": self.to_email,
            "reason": self.reason,
        }
        for key, value in equals.items():
            if not value:
                continue
            result.append(f'{key}="{value}"')

        if self.status:
            statuses = [f"'{s.value}'" for s in self.status]
            result.append(f"status IN ({','.join(statuses)})")

        if self.message_created_at:
            result.extend([created_at.to_str() for created_at in self.message_created_at])

        return " AND ".join(result)


__exports__ = ()
