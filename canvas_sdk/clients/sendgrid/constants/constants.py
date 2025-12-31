from dataclasses import dataclass


@dataclass(frozen=True)
class _Constants:
    """Internal constants for SendGrid integration."""

    rfc3339_format: str = "%Y-%m-%dT%H:%M:%SZ"


Constants = _Constants()

__exports__ = ()
