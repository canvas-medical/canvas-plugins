from typing import Literal
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import Coding
from canvas_sdk.v1.data import ReasonForVisitSettingCoding


class ReasonForVisitCommand(_BaseCommand):
    """A class for managing a ReasonForVisit command within a specific note."""

    class Meta:
        key = "reasonForVisit"

    structured: bool = False
    coding: Coding | UUID | str | None = None
    comment: str | None = None

    def _get_error_details(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if self.structured and not self.coding:
            errors.append(
                self._create_error_detail(
                    "value", "Structured RFV should have a coding.", self.coding
                )
            )

        if self.coding:
            if isinstance(self.coding, str | UUID):
                query = {"id": self.coding}
                error_message = f"ReasonForVisitSettingCoding with id {self.coding} does not exist."
            else:
                query = {"code": self.coding["code"], "system": self.coding["system"]}
                error_message = f"ReasonForVisitSettingCoding with code {self.coding['code']} and system {self.coding['system']} does not exist."
            if not ReasonForVisitSettingCoding.objects.filter(**query).exists():
                errors.append(self._create_error_detail("value", error_message, self.coding))
        return errors

    @classmethod
    def command_schema(cls) -> dict:
        """The schema of the command."""
        command_schema = super().command_schema()
        # the commands api does not include the 'structured' field in the fields response
        command_schema.pop("structured")
        return command_schema


__exports__ = ("ReasonForVisitCommand",)
