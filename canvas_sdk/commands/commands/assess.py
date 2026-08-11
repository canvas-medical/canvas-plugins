from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.v1.data import Command, Condition, Note

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

    def _is_target_patient(self, patient_id: str) -> bool:
        """Return whether the given patient is the one whose chart this command writes to."""
        if self.note_uuid:
            return Note.objects.filter(id=self.note_uuid, patient__id=patient_id).exists()

        if self.command_uuid:
            return Command.objects.filter(id=self.command_uuid, patient__id=patient_id).exists()

        return True

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
