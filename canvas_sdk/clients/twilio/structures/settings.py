from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Twilio account settings containing authentication credentials."""

    account_sid: str
    key: str
    secret: str


__exports__ = ()
