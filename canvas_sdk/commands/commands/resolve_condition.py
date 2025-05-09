from typing import Literal
from uuid import UUID

from django.db.models.expressions import Subquery
from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.v1.data import Condition, Note


class ResolveConditionCommand(BaseCommand):
    """A class for managing a ResolveCondition command within a specific note."""

    class Meta:
        key = "resolveCondition"

    condition_id: UUID | str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "condition"}
    )
    show_in_condition_list: bool = False
    rationale: str | None = Field(max_length=1024, default=None)

    def _get_error_details(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.condition_id:
            subquery = Subquery(Note.objects.filter(id=self.note_uuid).values("patient_id")[:1])
            if (
                not Condition.objects.active()
                .filter(id=self.condition_id, patient=subquery)
                .exists()
            ):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Condition with id {self.condition_id} does not exist.",
                        self.condition_id,
                    )
                )

        return errors


__exports__ = ("ResolveConditionCommand",)
