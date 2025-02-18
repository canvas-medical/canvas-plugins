from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.commands.goal import GoalCommand


class CloseGoalCommand(BaseCommand):
    """A class for managing a CloseGoal command within a specific note."""

    class Meta:
        key = "closeGoal"
        commit_required_fields = ("goal_id",)

    goal_id: int | None = None
    achievement_status: GoalCommand.AchievementStatus | None = None
    progress: str | None = None
