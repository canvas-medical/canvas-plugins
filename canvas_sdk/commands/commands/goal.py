from datetime import date, datetime
from enum import StrEnum

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class GoalCommand(_BaseCommand):
    """A class for managing a Goal command within a specific note."""

    class Meta:
        key = "goal"

    class Priority(StrEnum):
        HIGH = "high-priority"
        MEDIUM = "medium-priority"
        LOW = "low-priority"

    class AchievementStatus(StrEnum):
        IN_PROGRESS = "in-progress"
        IMPROVING = "improving"
        WORSENING = "worsening"
        NO_CHANGE = "no-change"
        ACHIEVED = "achieved"
        SUSTAINING = "sustaining"
        NOT_ACHIEVED = "not-achieved"
        NO_PROGRESS = "no-progress"
        NOT_ATTAINABLE = "not-attainable"

    goal_statement: str = ""
    start_date: date = Field(default_factory=lambda: datetime.now().date())
    due_date: date | None = None
    achievement_status: AchievementStatus | None = None
    priority: Priority | None = None
    progress: str | None = None


__exports__ = ("GoalCommand",)
