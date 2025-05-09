from datetime import datetime
from enum import Enum

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


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

    goal_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "goal_statement"}
    )
    due_date: datetime | None = None
    achievement_status: AchievementStatus | None = None
    priority: Priority | None = None
    progress: str | None = None


__exports__ = ("UpdateGoalCommand",)
