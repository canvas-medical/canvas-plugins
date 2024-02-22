from pydantic import model_validator
from typing_extensions import Self

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import Coding


class ReasonForVisitCommand(_BaseCommand):
    """A class for managing a ReasonForVisit command within a specific note."""

    structured: bool = False
    # how do we make sure that coding is a valid rfv coding from their home-app?
    coding: Coding | None = None
    comment: str | None = None

    @model_validator(mode="after")
    def _verify_structured_has_a_coding(self) -> Self:
        if self.structured and not self.coding:
            raise ValueError("Structured RFV should have a coding.")
        return self

    @property
    def values(self) -> dict:
        """The ReasonForVisit command's field values."""
        return {"structured": self.structured, "coding": self.coding, "comment": self.comment}
