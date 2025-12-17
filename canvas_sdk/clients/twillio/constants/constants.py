from dataclasses import dataclass


@dataclass(frozen=True)
class _Constants:
    """Configuration constants for Twilio SMS client.

    Attributes:
        sms_max_length: Maximum length of SMS message text (1600 characters).
        standard_date: ISO 8601 date format string.
        twilio_date: Twilio API date format string.
    """

    sms_max_length: int = 1600
    standard_date: str = "%Y-%m-%dT%H:%M:%S%z"
    twilio_date: str = "%a, %d %b %Y %H:%M:%S %z"


Constants = _Constants()

__exports__ = ()
