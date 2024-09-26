from datetime import datetime
from enum import Enum

from canvas_sdk.commands.base import _BaseCommand


class GoalCommand(_BaseCommand):
    """A class for managing a Goal command within a specific note."""

    class Meta:
        key = "goal"
        commit_required_fields = ("goal_statement", "start_date")

    class Priority(Enum):
        HIGH = "high-priority"
        MEDIUM = "medium-priority"
        LOW = "low-priority"

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

    goal_statement: str = ""
    start_date: datetime = datetime.now()
    due_date: datetime | None = None
    achievement_status: AchievementStatus | None = None
    priority: Priority | None = None
    progress: str | None = None

    @property
    def values(self) -> dict:
        """The Goal command's field values."""
        return {
            "goal_statement": self.goal_statement,
            "start_date": (self.start_date.isoformat() if self.start_date else None),
            "due_date": (self.due_date.isoformat() if self.due_date else None),
            "achievement_status": (
                self.achievement_status.value if self.achievement_status else None
            ),
            "priority": (self.priority.value if self.priority else None),
            "progress": self.progress,
        }
