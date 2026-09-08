from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand, _OptionalId
from canvas_sdk.v1.data import Goal


class UpdateGoalCommand(_BaseCommand):
    """A class for managing an UpdateGoal command within a specific note."""

    class Meta:
        key = "updateGoal"

    class AchievementStatus(Enum):
        IN_PROGRESS = "in-progress"
        IMPROVING = "improving"
        WORSENING = "worsening"
        NO_CHANGE = "no-change"
        ACHIEVED = "achieved"
        SUSTAINING = "sustaining"
        NOT_ACHIEVED = "not-achieved"
        NO_PROGRESS = "no-progress"
        NOT_ATTAINABLE = "not-attainable"

    class Priority(Enum):
        HIGH = "high-priority"
        MEDIUM = "medium-priority"
        LOW = "low-priority"

    goal_id: _OptionalId = Field(
        default=None, json_schema_extra={"commands_api_name": "goal_statement"}
    )
    due_date: datetime | None = None
    achievement_status: AchievementStatus | None = None
    priority: Priority | None = None
    progress: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Check that the goal being updated is one this patient has.

        Nothing else does: a goal named by id is applied as given, and the values missing from the
        command are then filled in from it. An unowned id would therefore copy one patient's due
        date and priority onto another patient's note, rather than simply being dropped.

        The patient is resolved from the note or, on an edit, from the command itself. When neither
        is persisted yet there is nothing to compare against and the check is skipped, so a plugin
        returning several effects at once still works.
        """
        errors = super()._get_error_details(method)

        if self.goal_id is None:
            return errors

        patient_id = self._anchor_patient_id()

        if patient_id is None:
            return errors

        if not Goal.objects.filter(id=self.goal_id, patient__id=patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Goal {self.goal_id} not found or not associated with the patient.",
                    self.goal_id,
                )
            )

        return errors


__exports__ = ("UpdateGoalCommand",)
