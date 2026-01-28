from enum import Enum


class MessageDirection(Enum):
    """Enum representing the direction of a Twilio message (inbound or various outbound types)."""

    INBOUND = "inbound"
    OUTBOUND_API = "outbound-api"
    OUTBOUND_CALL = "outbound-call"
    OUTBOUND_REPLY = "outbound-reply"


__exports__ = ()
