from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.commands.goal import GoalCommand
from canvas_sdk.v1.data import Goal


class CloseGoalCommand(BaseCommand):
    """A class for managing a CloseGoal command within a specific note."""

    class Meta:
        key = "closeGoal"

    goal_id: int | None = None
    achievement_status: GoalCommand.AchievementStatus | None = None
    progress: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Check that the goal being closed is one this patient has.

        Only ownership is checked. The patient is resolved from the note or, on an edit, from the
        command itself; when neither is persisted yet there is nothing to compare against and the
        check is skipped, so a plugin returning several effects at once still works.
        """
        errors = super()._get_error_details(method)

        if self.goal_id is None or (patient_id := self._anchor_patient_id()) is None:
            return errors

        if not Goal.objects.filter(dbid=self.goal_id, patient__id=patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Goal {self.goal_id} not found or not associated with the patient.",
                    self.goal_id,
                )
            )

        return errors


__exports__ = ("CloseGoalCommand",)
