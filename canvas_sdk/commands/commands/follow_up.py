from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import Coding
from canvas_sdk.v1.data import NoteType, ReasonForVisitSettingCoding


class FollowUpCommand(_BaseCommand):
    """A class for managing a Follow-Up command within a specific note."""

    class Meta:
        key = "followUp"

    structured: bool = False
    requested_date: date | None = None
    note_type_id: UUID | str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "note_type"}
    )
    reason_for_visit: Coding | UUID | str | None = None
    comment: str | None = None

    def _get_error_details(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.reason_for_visit:
            if self.structured:
                if isinstance(self.reason_for_visit, str | UUID):
                    query = {"id": self.reason_for_visit}
                    error_message = f"ReasonForVisitSettingCoding with id {self.reason_for_visit} does not exist."
                else:
                    query = {
                        "code": self.reason_for_visit["code"],
                        "system": self.reason_for_visit["system"],
                    }
                    error_message = f"ReasonForVisitSettingCoding with code {self.reason_for_visit['code']} and system {self.reason_for_visit['system']} does not exist."

                if not ReasonForVisitSettingCoding.objects.filter(**query).exists():
                    errors.append(
                        self._create_error_detail("value", error_message, self.reason_for_visit)
                    )
            elif not isinstance(self.reason_for_visit, str):
                errors.append(
                    self._create_error_detail(
                        "value",
                        "reason for visit must be a string when structured is False.",
                        self.reason_for_visit,
                    )
                )

        if (
            self.note_type_id
            and not NoteType.objects.filter(
                id=self.note_type_id, is_active=True, is_scheduleable=True
            ).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"NoteType with id {self.note_type_id} does not exist or is not scheduleable.",
                    self.note_type_id,
                )
            )

        return errors


__exports__ = ("FollowUpCommand",)
