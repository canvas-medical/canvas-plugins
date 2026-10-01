from datetime import date
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.v1.data import Condition

CONDITION_VALIDATED_METHODS = frozenset({"originate", "edit"})


class AssessCommand(_BaseCommand):
    """A class for managing an Assess command within a specific note.

    Name the condition either by `condition_id`, for a condition already on the patient's chart,
    or by `icd10_code`, which reuses the patient's charted condition with that code or records a
    new one. Leaving `show_in_problem_list` unset keeps the condition's current problem list status
    (new conditions go on the problem list).
    """

    class Meta:
        key = "assess"

    class Status(Enum):
        IMPROVED = "improved"
        STABLE = "stable"
        DETERIORATED = "deteriorated"

    condition_id: UUID | str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "condition"}
    )
    icd10_code: str | None = None
    approximate_date_of_onset: date | None = None
    show_in_problem_list: bool | None = None
    background: str | None = None
    status: Status | None = None
    narrative: str | None = Field(default=None, max_length=2048)

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method not in CONDITION_VALIDATED_METHODS:
            return errors

        if self.condition_id and self.icd10_code:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Name the condition with either condition_id or icd10_code, not both",
                    self.icd10_code,
                )
            )
            return errors

        if not self.condition_id:
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
