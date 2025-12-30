from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Represents SendGrid API configuration settings."""

    key: str


__exports__ = ()
