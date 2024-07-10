from typing import Literal

from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import Coding


class ReasonForVisitCommand(_BaseCommand):
    """A class for managing a ReasonForVisit command within a specific note."""

    class Meta:
        key = "reasonForVisit"

    structured: bool = False
    # how do we make sure that coding is a valid rfv coding from their home-app?
    coding: Coding | None = None
    comment: str | None = None

    def _get_error_details(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if self.structured and not self.coding:
            errors.append(
                self._create_error_detail(
                    "value", f"Structured RFV should have a coding.", self.coding
                )
            )
        return errors

    @classmethod
    def command_schema(cls) -> dict:
        """The schema of the command."""
        command_schema = super().command_schema()
        # the commands api does not include the 'structured' field in the fields response
        command_schema.pop("structured")
        return command_schema

    @property
    def values(self) -> dict:
        """The ReasonForVisit command's field values."""
        return {"structured": self.structured, "coding": self.coding, "comment": self.comment}
