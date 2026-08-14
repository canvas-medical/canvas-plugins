from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.v1.data import Condition

CONDITION_VALIDATED_METHODS = frozenset({"originate", "edit"})


class AssessCommand(_BaseCommand):
    """A class for managing an Assess command within a specific note."""

    class Meta:
        key = "assess"

    class Status(Enum):
        IMPROVED = "improved"
        STABLE = "stable"
        DETERIORATED = "deteriorated"

    condition_id: UUID | str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "condition"}
    )
    background: str | None = None
    status: Status | None = None
    narrative: str | None = Field(default=None, max_length=2048)

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not self.condition_id or method not in CONDITION_VALIDATED_METHODS:
            return errors

        condition_patient_id = (
            Condition.objects.filter(id=self.condition_id)
            .values_list("patient__id", flat=True)
            .first()
        )

        if condition_patient_id is None or not self._is_target_patient(condition_patient_id):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Condition {self.condition_id} does not belong to this command's patient",
                    self.condition_id,
                )
            )

        return errors


__exports__ = ("AssessCommand",)
