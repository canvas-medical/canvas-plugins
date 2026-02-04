from enum import Enum


class StatusEmail(Enum):
    """Defines the possible status values for an email in SendGrid."""

    PROCESSED = "processed"
    DELIVERED = "delivered"
    NOT_DELIVERED = "not_delivered"
    DEFERRED = "deferred"
    DROPPED = "dropped"
    BOUNCED = "bounced"
    BLOCKED = "blocked"


__exports__ = ()
