from enum import Enum


class EventEmail(Enum):
    """Defines the types of events that can occur for an email in SendGrid."""

    BOUNCE = "bounce"
    CLICK = "click"
    DEFERRED = "deferred"
    DELIVERED = "delivered"
    DROPPED = "dropped"
    CANCEL_DROP = "cancel_drop"
    OPEN = "open"
    PROCESSED = "processed"
    RECEIVED = "received"
    SPAM_REPORT = "spamreport"
    GROUP_UNSUBSCRIBE = "group_unsubscribe"
    GROUP_RESUBSCRIBE = "group_resubscribe"
    UNSUBSCRIBE = "unsubscribe"


__exports__ = ()
