from typing import Literal

from pydantic import BaseModel, ConfigDict


class Recommendation(BaseModel):
    """
    A Recommendation for a Protocol Card.
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    title: str = ""
    button: str = ""
    href: str | None = None
    command: str | None = None
    context: dict | None = None

    @property
    def values(self) -> dict:
        """The ProtocolCard recommendation's values."""
        return {
            "title": self.title,
            "button": self.button,
            "href": self.href,
            "command": {"type": self.command} if self.command else {},
            "context": self.context or {},
        }
