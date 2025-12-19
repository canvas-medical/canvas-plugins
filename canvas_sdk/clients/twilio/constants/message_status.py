from enum import Enum


class MessageStatus(Enum):
    """Enum representing the various statuses a Twilio message can have throughout its lifecycle."""

    ACCEPTED = "accepted"
    SCHEDULED = "scheduled"
    CANCELED = "canceled"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    UNDELIVERED = "undelivered"
    PARTIALLY_DELIVERED = "partially_delivered"
    RECEIVING = "receiving"
    RECEIVED = "received"
    READ = "read"


__exports__ = ()
