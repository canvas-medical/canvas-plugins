from enum import Enum


class DateOperation(Enum):
    """Enum representing date filtering operations for querying Twilio messages."""

    ON_EXACTLY = "ON"
    ON_AND_BEFORE = "BEFORE"
    ON_AND_AFTER = "AFTER"


__exports__ = ()
